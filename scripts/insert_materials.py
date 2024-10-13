# scripts/insert_materials.py

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Material


# 批量插入物料表的数据
def insert_materials():
    # 定义要插入的物料数据
    materials = [
        {'material_code': '20000', 'name': '眼镜', 'unit': '副', 'allocation_method': '生产', 'loss_rate': 0.00, 'lead_time': 1},
        {'material_code': '20109', 'name': '螺钉', 'unit': '个', 'allocation_method': '采购', 'loss_rate': 0.10, 'lead_time': 0},
        {'material_code': '20100', 'name': '镜框', 'unit': '副', 'allocation_method': '生产', 'loss_rate': 0.00, 'lead_time': 2},
        {'material_code': '20110', 'name': '镜架', 'unit': '个', 'allocation_method': '采购', 'loss_rate': 0.00, 'lead_time': 0},
        {'material_code': '20120', 'name': '镜腿', 'unit': '个', 'allocation_method': '采购', 'loss_rate': 0.00, 'lead_time': 0},
        {'material_code': '20130', 'name': '鼻托', 'unit': '个', 'allocation_method': '采购', 'loss_rate': 0.00, 'lead_time': 0},
        {'material_code': '20300', 'name': '镜片', 'unit': '片', 'allocation_method': '采购', 'loss_rate': 0.00, 'lead_time': 0},
    ]

    # 将物料数据插入 Material 表中
    for item in materials:
        Material.objects.create(
            material_id=item['material_code'],  # 使用 material_id 作为物料号
            name=item['name'],
            unit=item['unit'],
            allocation_method=item['allocation_method'],
            loss_rate=item['loss_rate'],
            lead_time=item['lead_time']
        )

    print("物料数据插入成功！")  # 输出插入成功消息


# 执行插入操作
if __name__ == '__main__':
    insert_materials()  # 运行插入函数
