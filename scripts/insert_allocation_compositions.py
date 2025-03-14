# scripts/insert_boms.py
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import AllocationComposition, Material


def insert_allocation_compositions():
    # 定义要插入的调配构成数据
    allocations = [
        {'base_code': '000001', 'region_code': 'L001', 'parent_material_name': '眼镜',
         'child_material_name': '镜框', 'quantity': 1, 'allocation_lead_time': 0, 'supplier_lead_time': 0},
        {'base_code': '000001', 'region_code': 'L001', 'parent_material_name': '眼镜',
         'child_material_name': '镜片', 'quantity': 2, 'allocation_lead_time': 1, 'supplier_lead_time': 20},
        {'base_code': '000001', 'region_code': 'L001', 'parent_material_name': '眼镜',
         'child_material_name': '螺钉', 'quantity': 2, 'allocation_lead_time': 1, 'supplier_lead_time': 10},
        {'base_code': '000001', 'region_code': 'L003', 'parent_material_name': '镜框',
         'child_material_name': '镜架', 'quantity': 1, 'allocation_lead_time': 1, 'supplier_lead_time': 20},
        {'base_code': '000001', 'region_code': 'L003', 'parent_material_name': '镜框',
         'child_material_name': '镜腿', 'quantity': 2, 'allocation_lead_time': 1, 'supplier_lead_time': 10},
        {'base_code': '000001', 'region_code': 'L003', 'parent_material_name': '镜框',
         'child_material_name': '鼻托', 'quantity': 2, 'allocation_lead_time': 1, 'supplier_lead_time': 18},
        {'base_code': '000001', 'region_code': 'L003', 'parent_material_name': '镜框',
         'child_material_name': '螺钉', 'quantity': 4, 'allocation_lead_time': 1, 'supplier_lead_time': 10}
    ]

    # 插入数据到 AllocationComposition 表中
    for allocation in allocations:
        # 获取父物料和子物料的实例
        parent_material = Material.objects.get(name=allocation['parent_material_name'])
        child_material = Material.objects.get(name=allocation['child_material_name'])

        AllocationComposition.objects.create(
            base_code=allocation['base_code'],
            region_code=allocation['region_code'],
            parent_material_code=parent_material,  # 使用外键
            parent_material_name=allocation['parent_material_name'],
            child_material_code=child_material,  # 使用外键
            child_material_name=allocation['child_material_name'],
            quantity=allocation['quantity'],
            allocation_lead_time=allocation['allocation_lead_time'],
            supplier_lead_time=allocation['supplier_lead_time']
        )

    print("调配构成数据插入成功！")  # 输出插入成功消息


if __name__ == '__main__':
    insert_allocation_compositions()  # 运行插入函数
