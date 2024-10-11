# scripts/insert_BOMs.py

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import BillOfMaterial


# 批量插入BOM表的数据
def insert_bom_data():
    bom_data = [
        {'part_number': '20100', 'description': '镜框', 'quantity': 1, 'unit': '个', 'level': 1},
        {'part_number': '20110', 'description': '镜架', 'quantity': 1, 'unit': '个', 'level': 2},
        {'part_number': '20120', 'description': '镜腿', 'quantity': 2, 'unit': '个', 'level': 2},
        {'part_number': '20130', 'description': '鼻托', 'quantity': 2, 'unit': '个', 'level': 2},
        {'part_number': '20109', 'description': '螺钉', 'quantity': 4, 'unit': '个', 'level': 2},
        {'part_number': '20300', 'description': '镜片', 'quantity': 2, 'unit': '个', 'level': 1},
        {'part_number': '20109', 'description': '螺钉', 'quantity': 2, 'unit': '个', 'level': 1},
    ]

    for item in bom_data:
        BillOfMaterial.objects.create(
            part_number=item['part_number'],
            description=item['description'],
            quantity=item['quantity'],
            unit=item['unit'],
            level=item['level']
        )

    print("BOM数据插入成功！")


# 执行插入操作
if __name__ == '__main__':
    insert_bom_data()
