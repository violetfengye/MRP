# 需求计算函数，使用已经加载的 allinventories 字典
import math
from datetime import timedelta

from myapp.models import AllocationComposition
from myapp.views import allinventories


def calculate_material_requirements(material, required_quantity, due_date):
    # 该 material_mrp_results 用于存储当前物料和其所有子物料的计算结果
    material_mrp_results = []

    allo_records = AllocationComposition.objects.filter(parent_material_name=material.name)

    if not allo_records.exists():
        # 如果当前物料没有子物料

        # 从字典中获取库存信息
        current_inventory = allinventories.get(material.material_id, 0)

        if current_inventory:
            if current_inventory > required_quantity:
                allinventories[material.material_id] -= required_quantity
                required_quantity = 0
            else:
                required_quantity -= current_inventory
                allinventories[material.material_id] = 0

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
                                                                     completion_date)

        material_mrp_results.extend(child_material_mrp_results)

    return material_mrp_results  # 返回当前物料及其子物料的 MRP 计算结果
