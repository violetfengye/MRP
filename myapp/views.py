import math

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from datetime import timedelta
from .forms import MPSRecordForm
from collections import defaultdict


def main_page(request):
    # Render the main page template with buttons
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


# 显示 MRP 查询表单的视图
def mrp_query(request):
    if request.method == 'POST':
        mps_id = request.POST.get('mps_id')
        return redirect('mrp_results', mps_id=mps_id)  # 重定向到结果页面
    return render(request, 'mrp_query.html')


# 处理 MRP 计算并显示结果的视图
def mrp_results(request, mps_id):
    try:
        mps_record = MPSRecord.objects.get(mps_id=mps_id)
        # 执行 MRP 计算
        mrp_final_results = calculate_mrp(mps_record)  # 通过 mps_record 计算 MRP
        return render(request, 'mrp_results.html', {'mrp_results': mrp_final_results})
    except MPSRecord.DoesNotExist:
        return render(request, 'mrp_query.html', {'error': 'MPS 记录未找到'})


# 假设这个字典将保存所有的库存信息
allinventories = {}


# 从数据库中加载所有库存信息到字典
def load_all_inventory():
    inventories = Inventory.objects.all()
    for inv in inventories:
        total_inventory = inv.workshop_inventory + inv.material_inventory
        allinventories[inv.material_code] = total_inventory


# MRP 计算函数
def calculate_mrp(mps_record):
    # 获取 MPS 记录的产品、数量和完工日期
    material = mps_record.material_name
    required_quantity = mps_record.required_quantity
    due_date = mps_record.due_date

    # 创建一个仓库表映射，加载一次库存数据
    load_all_inventory()

    # 递归计算需求
    # 这里的 mrp_final_results 是整个 MRP 计算的最终结果，包括所有物料的需求信息
    mrp_final_results = calculate_material_requirements(material, required_quantity, due_date)

    # 清空字典，准备重新填充
    allinventories.clear()

    return mrp_final_results


# 需求计算函数，使用已经加载的 allinventories 字典
def calculate_material_requirements(material, required_quantity, due_date):
    # 该 material_mrp_results 用于存储当前物料和其所有子物料的计算结果
    material_mrp_results = []

    allo_records = AllocationComposition.objects.filter(parent_material_name=material.name)

    if not allo_records.exists():
        # 如果当前物料没有子物料

        # 从字典中获取库存信息
        current_inventory = allinventories.get(material, 0)

        if current_inventory:
            if current_inventory > required_quantity:
                allinventories[material] -= required_quantity
                required_quantity = 0
            else:
                required_quantity -= current_inventory
                allinventories[material] = 0

        # 根据调配方式计算日期
        if material.allocation_method == '生产':
            completion_date = due_date
            start_date = completion_date - timedelta(days=material.lead_time)
        elif material.allocation_method == '采购':
            completion_date = due_date
            allomaterial = AllocationComposition.objects.filter(child_material_name=material.name).first()
            start_date = completion_date - timedelta(
                days=material.lead_time + allomaterial.allocation_lead_time + allomaterial.supplier_lead_time)

        material_mrp_results.append({
            'allocation_method': material.allocation_method,
            'material_code': material.material_id,
            'material_name': material.name,
            'required_quantity': required_quantity,
            'start_date': start_date,
            'completion_date': completion_date
        })

        return material_mrp_results

    # 既然有子物料，那么一定是生产方式
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

    for allo in allo_records:
        child_material = allo.child_material_code
        child_quantity = allo.quantity
        # 计算子物料的需求数量
        required_child_quantity = math.ceil(required_quantity * child_quantity / (1 - child_material.loss_rate))
        # 递归计算子物料的需求
        # 该 child_material_mrp_results 存储子物料的 MRP 计算结果，然后被添加到 material_mrp_results 中
        child_material_mrp_results = calculate_material_requirements(child_material, required_child_quantity,
                                                                     start_date)

        material_mrp_results.extend(child_material_mrp_results)

    return material_mrp_results  # 返回当前物料及其子物料的 MRP 计算结果
