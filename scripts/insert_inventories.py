# scripts/insert_inventories.py

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Inventory


#批量插入库存表的数据
def insert_inventories():
    inventories = [
        {'material_code': '20000', 'material_name': '眼镜', 'workshop_stock': 0, 'material_stock': 0},
        {'material_code': '20109', 'material_name': '螺钉', 'workshop_stock': 10, 'material_stock': 50},
        {'material_code': '20100', 'material_name': '镜框', 'workshop_stock': 0, 'material_stock': 0},
        {'material_code': '20110', 'material_name': '镜架', 'workshop_stock': 0, 'material_stock': 0},
        {'material_code': '20120', 'material_name': '镜腿', 'workshop_stock': 10, 'material_stock': 20},
        {'material_code': '20130', 'material_name': '鼻托', 'workshop_stock': 0, 'material_stock': 0},
        {'material_code': '20300', 'material_name': '镜片', 'workshop_stock': 0, 'material_stock': 0},
    ]

    for item in inventories:
        Inventory.objects.create(
            material_code=item['material_code'],
            material_name=item['material_name'],
            workshop_inventory=item['workshop_stock'],
            material_inventory=item['material_stock'],
        )

    print("库存数据插入成功！")


# 执行插入操作
if __name__ == '__main__':
    insert_inventories()
