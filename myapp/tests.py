import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()


from myapp.models import Inventory

allinventories = {}


# 从数据库中加载所有库存信息到字典
def load_all_inventory():
    inventories = Inventory.objects.all()
    for inv in inventories:
        total_inventory = inv.workshop_inventory + inv.material_inventory
        allinventories[inv.material_code] = total_inventory


if __name__ == '__main__':
    load_all_inventory()
    print(allinventories)  # 运行插入函数


