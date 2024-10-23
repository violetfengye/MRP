# 处理 MRP 计算并显示结果的视图
import math
from datetime import timedelta
from logging import fatal

from django.shortcuts import render
from django.utils.functional import empty

from myapp.models import AllocationComposition, Inventory, MPSRecord, Material


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

def isempty_inventory(inventory):
    for material_name, total_inventory in inventory.items():
        if total_inventory > 0:
            return material_name  # 返回有库存的物料名称
    return 'empty_inventory'  # 如果没有库存则返回这个标识符


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
            all_mrp_results.append({
                'mps_id': mps_record.mps_id,
                'mrp_results': mrp_results
            })
        except Exception as e:
            print(f"Error calculating MRP for MPS ID {mps_record.mps_id}: {e}")
            continue

    allinventories.clear()  # 清空缓存
    cnt = 0
    return adjust_requirement(all_mrp_results)


# 初始需求计算函数，使用已经加载的 allinventories 字典
def calculate_material_requirements(material, required_quantity, due_date, father_id=-1):
    global cnt
    material_mrp_results = []
    allo_records = AllocationComposition.objects.filter(parent_material_name=material.name)

    # 只有采购才没有子物料
    if not allo_records.exists():
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
            'completion_date': completion_date,
            'mid':cnt,
            'father_id': father_id,
        })
        cnt += 1

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
    })

    for allo in allo_records:
        child_material = allo.child_material_code
        child_quantity = allo.quantity
        required_child_quantity = math.ceil(required_quantity * child_quantity / (1 - child_material.loss_rate))
        father_id = cnt
        cnt += 1
        child_material_mrp_results = calculate_material_requirements(child_material, required_child_quantity,
                                                                     start_date,father_id)

        material_mrp_results.extend(child_material_mrp_results)

    return material_mrp_results


def adjust_requirement(all_mrp_results):

    # 直接通过生成器遍历所有 mrp_results 并加入 trueneeds 列表
    trueneeds = [result for entry in all_mrp_results for result in entry['mrp_results']]

    # 初始化哈希表，存储物料是否已更新需求
    material_status = {trueneed['mid']: False for trueneed in trueneeds}
    changes = {trueneed['mid']: 0 for trueneed in trueneeds}
    material_status[trueneeds[0]['mid']] = True  # 确保根物料需求被标记为已更新

    # 根据开始时间对需求排序，确保先处理较早的需求
    trueneeds_sorted = sorted(trueneeds, key=lambda x: x['start_date'])

    # 只遍历有库存的物料，避免每次循环都遍历所有库存
    while any(allinventories.values()):  # 判断是否还有剩余库存
        tmp_name = next((name for name, inv in allinventories.items() if inv > 0), None)  # 获取有库存的物料名称

        if tmp_name is None:
            break  # 没有可用库存时跳出循环

        for trueneed in trueneeds_sorted:
            if trueneed['material_name'] == tmp_name:
                current_inventory = allinventories[tmp_name]
                required_qty = trueneed['required_quantity']

                # 根据库存量调整需求量
                if current_inventory >= required_qty:
                    allinventories[tmp_name] -= required_qty
                    changes[trueneed['mid']] = required_qty
                    trueneed['required_quantity'] = 0  # 需求已满足
                else:
                    trueneed['required_quantity'] -= current_inventory
                    changes[trueneed['mid']] = current_inventory
                    allinventories[tmp_name] = 0  # 库存耗尽

    # 按照 mid 排序，确保父物料在子物料前面处理
    trueneeds_final = sorted(trueneeds, key=lambda x: x['mid'])

    # 递归更新子物料需求
    for trueneed in trueneeds_final:
        if not material_status[trueneed['mid']]:
            father_id = trueneed.get('father_id')
            if father_id and material_status[father_id]:  # 确保父物料已经更新
                trueneed['required_quantity'] -= changes[father_id]  # 根据父物料的变化调整子物料需求
                changes[trueneed['mid']] += changes[father_id]
                material_status[trueneed['mid']] = True  # 标记当前物料已更新












