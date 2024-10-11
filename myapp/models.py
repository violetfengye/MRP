from django.db import models


# Create your models here.
# 在models.py中定义模型

class BillOfMaterial(models.Model):
    part_number = models.CharField(max_length=10, verbose_name="零件号")
    description = models.CharField(max_length=50, verbose_name="描述")
    quantity = models.IntegerField(verbose_name="装配数量")
    unit = models.CharField(max_length=2, verbose_name="单位")
    level = models.IntegerField(verbose_name="层次")

    def __str__(self):
        return f"{self.part_number} - {self.description}"


class Material(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    name = models.CharField(max_length=20, verbose_name="名称")
    unit = models.CharField(max_length=5, verbose_name="单位")
    allocation_method = models.CharField(max_length=10, verbose_name="调配方式")
    loss_rate = models.FloatField(verbose_name="损耗率")
    lead_time = models.IntegerField(verbose_name="作业提前期")

    def __str__(self):
        return self.name


class AllocationComposition(models.Model):
    base_code = models.CharField(max_length=10, verbose_name="调配基准编号")
    region_code = models.CharField(max_length=10, verbose_name="调配区域代码")
    parent_material_code = models.CharField(max_length=10, verbose_name="父物料号")
    parent_material_name = models.CharField(max_length=20, verbose_name="父物料名称")
    child_material_code = models.CharField(max_length=10, verbose_name="子物料号")
    child_material_name = models.CharField(max_length=20, verbose_name="子物料名称")
    quantity = models.IntegerField(verbose_name="构成数量")
    allocation_lead_time = models.IntegerField(verbose_name="配料提前期")
    supplier_lead_time = models.IntegerField(verbose_name="供应商提前期")

    def __str__(self):
        return f"{self.parent_material_name} -> {self.child_material_name}"


class Inventory(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    material_name = models.CharField(max_length=20, verbose_name="物料名称")
    workshop_inventory = models.IntegerField(verbose_name="工序库存")
    material_inventory = models.IntegerField(verbose_name="资材库存")

    def __str__(self):
        return f"{self.material_name} 库存"
