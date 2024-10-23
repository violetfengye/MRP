import math
import heapq
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from datetime import timedelta
from .forms import MPSRecordForm, BSVarForm
from collections import defaultdict


# 主界面视图
def main_page(request):
    return render(request, 'main_page.html')


# MPS 数据输入视图
def mps_input(request):
    if request.method == 'POST':
        form = MPSRecordForm(request.POST)
        if form.is_valid():
            form.save()  # 将表单数据保存到数据库
            return redirect('mps_success')  # 重定向到成功页面或重新显示表单
    else:
        form = MPSRecordForm()

    return render(request, 'mps_input.html', {'form': form})


# MPS 成功页面视图
def mps_success(request):
    return render(request, 'mps_success.html')


# mps记录展示视图
def mps_display(request):
    all_mps_records = MPSRecord.objects.all()
    return render(request, 'mps_display.html', {'mps_records': all_mps_records})


# mps记录删除视图
def delete_mps_record(request, mps_id):
    mps_record = get_object_or_404(MPSRecord, mps_id=mps_id)
    if request.method == 'POST':
        mps_record.delete()  # 删除 MPS 记录
        messages.success(request, 'MPS 记录已成功删除！')  # 添加成功删除的消息
        return redirect('mps_display')  # 重定向到显示页面


# 显示 MRP 查询表单的视图
def mrp_query(request):
    mps_records = MPSRecord.objects.all()  # 获取所有 MPS 记录
    if request.method == 'POST':
        mps_ids = request.POST.getlist('mps_ids')  # 获取多个 MPS ID

        if not mps_ids:
            return redirect('error')  # 如果为空，跳转到错误页面

        return redirect('mrp_results', mps_ids=','.join(mps_ids))  # 将多个 ID 以逗号分隔传递
    return render(request, 'mrp_query.html', {'mps_records': mps_records})


# 错误视图
def error(request):
    return render(request, 'error.html')


# 库存展示视图
def inventories_display(request):
    allinventories = Inventory.objects.all()
    return render(request, 'inventories_display.html', {'allinventories': allinventories})


# 更新库存的视图
def update_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, material_name=inventory_id)

    if request.method == 'POST':
        # 获取表单数据，并进行验证
        workshop_inventory = request.POST.get('workshop_inventory')
        material_inventory = request.POST.get('material_inventory')

        if workshop_inventory is not None and material_inventory is not None:
            try:
                # 尝试将其转换为整数
                inventory.workshop_inventory = int(workshop_inventory)
                inventory.material_inventory = int(material_inventory)
                inventory.save()

                messages.success(request, f'库存 {inventory.material_name} 已更新成功！')
                return redirect('inventories_display')  # 重定向回到库存查看页面

            except ValueError:
                messages.error(request, '无效的库存输入，请输入有效的数字。')

        else:
            messages.error(request, '库存字段不能为空！')

    return render(request, 'inventories_display.html', {'inventory': inventory})


# 资产负债表展示的视图
def bs_display(request):
    balancesheets = BalanceSheet.objects.all()
    calculation_results = []  # 用于存储多个计算结果

    if request.method == 'POST':
        # 获取表单输入的变量名
        bs_vars = request.POST.get('item_name')
        if bs_vars:
            # 将输入的变量名按逗号分割
            bs_var_list = bs_vars.split(',')
            # 遍历每个变量名，调用计算函数
            for bs_var in bs_var_list:
                bs_var = bs_var.strip()  # 去掉前后的空格
                calculation_result = bs_var_cal(bs_var)
                calculation_results.append(f'{bs_var}: {calculation_result}')

    # 将 balancesheets 和多个计算结果传递到模板中
    return render(request, 'bs_display.html', {
        'balancesheets': balancesheets,
        'calculation_results': calculation_results,  # 传递多个结果
    })


# 资产负债的计算逻辑
def bs_var_cal(bs_var):
    balancesheet = BalanceSheet.objects.get(bs_var=bs_var)
    allbalancesheet = BalanceSheet.objects.all()
    ans = ""
    ans += bs_var + ' = '
    for bs in allbalancesheet:
        if bs.bs_toid == balancesheet.bs_id:
            ans += bs.bs_var + ' + '
    if not bs_var == ans[:-3]:
        ans = ans[:-2]
        return ans
    else:
        return f"变量 {bs_var} 没有相关公式"

# 处理 MRP 计算并显示结果的视图
def mrp_results(request, mps_ids):
    # 将多个 MPS IDs 解析成一个列表
    mps_ids_list = mps_ids.split(',')

    # 获取所有选中的 MPS 记录
    mps_records = MPSRecord.objects.filter(mps_id__in=mps_ids_list)

    if not mps_records.exists():
        return render(request, 'mrp_query.html', {'error': '未找到 MPS 记录'})

    # 调用批量 MRP 计算函数，传递整个 mps_records 集合
    all_mrp_results = calculate_mrp_for_multiple(mps_records)

    # 渲染模板并显示所有 MRP 计算结果
    return render(request, 'mrp_results.html', {'all_mrp_results': all_mrp_results})


# 假设这个字典将保存所有的库存信息
allinventories = {}

cnt = 0

# 从数据库中加载所有库存信息到字典
def load_all_inventory():
    inventories = Inventory.objects.all()
    for inv in inventories:
        total_inventory = inv.workshop_inventory + inv.material_inventory
        allinventories[inv.material_code] = total_inventory


# MRP 计算函数
def calculate_mrp_for_multiple(mps_records):
    load_all_inventory()  # 加载库存
    global cnt
    all_mrp_results = []  # 存储所有 MPS 记录的 MRP 结果

    for mps_record in mps_records:
        try:
            # 执行MRP计算
            mrp_results = calculate_material_requirements(mps_record.material_name, mps_record.required_quantity,
                                                          mps_record.due_date)
            all_mrp_results.extend(mrp_results)
        except Exception as e:
            print(f"Error calculating MRP for MPS ID {mps_record.mps_id}: {e}")
            continue
    all_mrp_results_final = adjust_requirements_optimized(all_mrp_results,allinventories)
    # print(all_mrp_results_final)
    allinventories.clear()  # 清空缓存
    cnt = 0
    return all_mrp_results_final


# 初始需求计算函数，使用已经加载的 allinventories 字典
def calculate_material_requirements(material, required_quantity, due_date, father_id=-1,father_name=None):
    global cnt
    material_mrp_results = []
    allo_records = AllocationComposition.objects.filter(parent_material_name=material.name)

    # 只有采购才没有子物料
    if not allo_records.exists():
        completion_date = due_date
        allo_material = AllocationComposition.objects.filter(child_material_name=material.name).first()
        start_date = completion_date - timedelta(
                days=material.lead_time + allo_material.allocation_lead_time + allo_material.supplier_lead_time)

        cnt += 1
        material_mrp_results.append({
            'allocation_method': material.allocation_method,
            'material_code': material.material_id,
            'material_name': material.name,
            'required_quantity': required_quantity,
            'start_date': start_date,
            'completion_date': completion_date,
            'mid':cnt,
            'father_id': father_id,
            'father_name': father_name,
        })


        return material_mrp_results

    completion_date = due_date
    start_date = completion_date - timedelta(days=material.lead_time)

    material_mrp_results.append({
        'allocation_method': material.allocation_method,
        'material_code': material.material_id,
        'material_name': material.name,
        'required_quantity': required_quantity,
        'start_date': start_date,
        'completion_date': completion_date,
        'mid':cnt,
        'father_id': father_id,
        'father_name': father_name,
    })

    father_id = cnt
    father_name = material.name

    for allo in allo_records:
        child_material = allo.child_material_code
        child_quantity = allo.quantity
        required_child_quantity = math.ceil(required_quantity * child_quantity / (1 - child_material.loss_rate))
        child_material_mrp_results = calculate_material_requirements(child_material, required_child_quantity,
                                                                     start_date,father_id,father_name)

        material_mrp_results.extend(child_material_mrp_results)

    return material_mrp_results


def adjust_requirements_optimized(all_mrp_results, all_inventories):

    # 初始化物料库存表
    inventory_map = {material.name: inventory for material, inventory in all_inventories.items()}

    # 初始化哈希表，存储物料是否已更新需求
    material_status = {result['mid']: False for result in all_mrp_results}
    changes = {result['mid']: 0 for result in all_mrp_results}

    # 初始化物料需求表和优先队列，按start_date排序需求
    priority_queue = []
    for result in all_mrp_results:
        heapq.heappush(priority_queue, (result['start_date'], result['mid'], result))


    # 逐步处理需求
    while priority_queue:
        start_date, mid, current_need = heapq.heappop(priority_queue)
        mid = current_need['mid']
        father_id = current_need['father_id']
        material_name = current_need['material_name']
        required_quantity = current_need['required_quantity']

        # 从库存中扣除需求量
        if material_name in inventory_map and inventory_map[material_name] > 0:
            available_inventory = inventory_map[material_name]
            print(available_inventory)
            if available_inventory >= required_quantity:
                inventory_map[material_name] -= required_quantity
                changes[mid] = required_quantity
                material_status[mid] = True  # 需求已更新
                current_need['required_quantity'] = 0  # 需求满足

            else:
                current_need['required_quantity'] -= available_inventory
                changes[mid] = available_inventory
                inventory_map[material_name] = 0  # 库存耗尽
                if father_id==-1:
                    material_status[mid] = True  # 需求已更新

        else:
            # 如果没有父物料或者父物料已经更新过了而且库存中没有该数据剩余则该数据已为最终结果
            if father_id==-1 or material_status[father_id]:
                material_status[mid] = True

    while not all(material_status.values()):
        for result in all_mrp_results:
            mid = result['mid']
            if material_status[mid]:
                continue
            father_id = result['father_id']
            child_quantity = AllocationComposition.objects.get(child_material_name=result['material_name'],parent_material_name=result['father_name']).quantity
            loss_rate = Material.objects.get(name=result['material_name']).loss_rate
            result['required_quantity'] -= math.ceil(changes[father_id] * child_quantity / (1 - loss_rate))
            material_status[mid] = True

    return all_mrp_results















