import math
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from datetime import timedelta
from .forms import MPSRecordForm
from collections import defaultdict


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


def mps_success(request):
    # MPS 成功页面视图
    return render(request, 'mps_success.html')


def mps_display(request):
    all_mps_records = MPSRecord.objects.all()
    return render(request, 'mps_display.html', {'mps_records': all_mps_records})


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


def error(request):
    return render(request, 'error.html')


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


# 定义一个排序函数，判断是否有子物料
def has_child_material(allo_record):
    # 检查中是否有该物料的子物料
    return AllocationComposition.objects.filter(parent_material_name=allo_record.child_material_name).exists()


# 假设这个字典将保存所有的库存信息
allinventories = {}


# 从数据库中加载所有库存信息到字典
def load_all_inventory():
    inventories = Inventory.objects.all()
    for inv in inventories:
        total_inventory = inv.workshop_inventory + inv.material_inventory
        allinventories[inv.material_code] = total_inventory


# MRP 计算函数
def calculate_mrp_for_multiple(mps_records):
    allinventories.clear()  # 清空缓存
    load_all_inventory()  # 加载库存

    all_mrp_results = []  # 存储所有 MPS 记录的 MRP 结果

    # 对 mps_records 按开始时间排序
    mps_records_sorted = sorted(mps_records, key=lambda x: x.due_date)

    for mps_record in mps_records_sorted:
        try:
            # 执行MRP计算
            mrp_results = calculate_material_requirements(mps_record.material_name, mps_record.required_quantity,
                                                          mps_record.due_date)
            all_mrp_results.append({
                'mps_id': mps_record.mps_id,
                'mrp_results': mrp_results
            })
        except Exception as e:
            print(f"Error calculating MRP for MPS ID {mps_record.mps_id}: {e}")
            continue

    allinventories.clear()  # 清空缓存
    return all_mrp_results


# 需求计算函数，使用已经加载的 allinventories 字典
def calculate_material_requirements(material, required_quantity, due_date):
    material_mrp_results = []
    allo_records = AllocationComposition.objects.filter(parent_material_name=material.name)

    if not allo_records.exists():
        current_inventory = allinventories.get(material, 0)

        if current_inventory:
            if current_inventory > required_quantity:
                allinventories[material] -= required_quantity
                required_quantity = 0
            else:
                required_quantity -= current_inventory
                allinventories[material] = 0

        if material.allocation_method == '生产':
            completion_date = due_date
            start_date = completion_date - timedelta(days=material.lead_time)
        elif material.allocation_method == '采购':
            completion_date = due_date
            allo_material = AllocationComposition.objects.filter(child_material_name=material.name).first()
            start_date = completion_date - timedelta(
                days=material.lead_time + allo_material.allocation_lead_time + allo_material.supplier_lead_time)

        material_mrp_results.append({
            'allocation_method': material.allocation_method,
            'material_code': material.material_id,
            'material_name': material.name,
            'required_quantity': required_quantity,
            'start_date': start_date,
            'completion_date': completion_date
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
        'completion_date': completion_date
    })

    allo_records = sorted(allo_records, key=lambda x: not has_child_material(x))

    for allo in allo_records:
        child_material = allo.child_material_code
        child_quantity = allo.quantity
        required_child_quantity = math.ceil(required_quantity * child_quantity / (1 - child_material.loss_rate))

        child_material_mrp_results = calculate_material_requirements(child_material, required_child_quantity,
                                                                     start_date)

        material_mrp_results.extend(child_material_mrp_results)

    return material_mrp_results


def inventories_display(request):
    allinventories = Inventory.objects.all()
    return render(request, 'inventories_display.html', {'allinventories': allinventories})


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


def delete_inventory(request, inventory_id):
    # 获取要删除的库存记录
    inventory = get_object_or_404(Inventory, id=inventory_id)

    if request.method == 'GET':
        inventory.delete()
        messages.success(request, f'库存 {inventory.material_name} 已删除成功！')
        return redirect('warehouse_view')  # 重定向回到库存查看页面
