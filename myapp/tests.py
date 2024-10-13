import math
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from datetime import timedelta
from .forms import MPSRecordForm
from collections import defaultdict


# 显示 MRP 查询表单的视图
def mrp_query(request):
    mps_records = MPSRecord.objects.all()  # 获取所有 MPS 记录
    if request.method == 'POST':
        mps_ids = request.POST.getlist('mps_ids')  # 获取多个 MPS ID
        return redirect('mrp_results', mps_ids=','.join(mps_ids))  # 将多个 ID 以逗号分隔传递
    return render(request, 'mrp_query.html', {'mps_records': mps_records})


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
