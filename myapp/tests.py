# 获取所有 allo_records
from myapp.models import AllocationComposition

allo_records = AllocationComposition.objects.all()

# 定义一个排序函数，判断是否有子物料
def has_child_material(allo_record):
    # 检查 BillOfMaterial 中是否有该物料的子物料
    return AllocationComposition.objects.filter(parent_material=allo_record.material).exists()

# 使用 sorted 对 allo_records 进行排序，有子物料的放前面，没子物料的放后面
sorted_allo_records = sorted(allo_records, key=lambda x: not has_child_material(x))

# 结果输出
for record in sorted_allo_records:
    print(f"Material: {record.material.name}, Has Child: {has_child_material(record)}")