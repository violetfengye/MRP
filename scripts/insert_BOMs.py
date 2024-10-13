# scripts/insert_BOMs.py

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import BillOfMaterial, Material


# 批量插入 BOM 表的数据
def insert_bom_data():
    # 定义要插入的 BOM 数据
    bom_data = [
        {'material_name': '眼镜', 'description': '眼镜', 'quantity': 0, 'unit': '个', 'level': 0},
        {'material_name': '镜框', 'description': '镜框', 'quantity': 1, 'unit': '个', 'level': 1},
        {'material_name': '镜架', 'description': '镜架', 'quantity': 1, 'unit': '个', 'level': 2},
        {'material_name': '镜腿', 'description': '镜腿', 'quantity': 2, 'unit': '个', 'level': 2},
        {'material_name': '鼻托', 'description': '鼻托', 'quantity': 2, 'unit': '个', 'level': 2},
        {'material_name': '螺钉', 'description': '螺钉', 'quantity': 4, 'unit': '个', 'level': 2},
        {'material_name': '镜片', 'description': '镜片', 'quantity': 2, 'unit': '个', 'level': 1},
        {'material_name': '螺钉', 'description': '螺钉', 'quantity': 2, 'unit': '个', 'level': 1},
    ]

    # 插入数据到 BillOfMaterial 表中
    for item in bom_data:
        # 获取物料的实例
        material = Material.objects.get(name=item['material_name'])

        BillOfMaterial.objects.create(
            material_id=material,  # 使用外键指向 Material 表中的实例
            description=item['description'],
            quantity=item['quantity'],
            unit=item['unit'],
            level=item['level']
        )

    print("BOM 数据插入成功！")  # 输出插入成功消息


# 执行插入操作
if __name__ == '__main__':
    insert_bom_data()  # 运行插入函数
