from django.db import models


# 在models.py中定义BOM模型，表示物料清单
class BillOfMaterial(models.Model):
    part_number = models.CharField(max_length=10, verbose_name="零件号")
    description = models.CharField(max_length=50, verbose_name="描述")
    quantity = models.IntegerField(verbose_name="装配数量")
    unit = models.CharField(max_length=2, verbose_name="单位")
    level = models.IntegerField(verbose_name="层次")  # 用于表示物料的层次结构

    def __str__(self):
        return f"{self.part_number} - {self.description}"  # 在Admin界面显示该模型的描述


# 物料模型，表示系统中每个物料的详细信息
class Material(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    name = models.CharField(max_length=20, verbose_name="名称")
    unit = models.CharField(max_length=5, verbose_name="单位")
    allocation_method = models.CharField(max_length=10, verbose_name="调配方式")
    loss_rate = models.FloatField(verbose_name="损耗率")
    lead_time = models.IntegerField(verbose_name="作业提前期")  # 作业前准备时间

    def __str__(self):
        return self.name


# 配料组成模型，定义父物料和子物料之间的关系
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
        return f"{self.parent_material_name} -> {self.child_material_name}"  # 显示父子物料关系


# 库存模型，表示每个物料的工序库存和资材库存
class Inventory(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    material_name = models.CharField(max_length=20, verbose_name="物料名称")
    workshop_inventory = models.IntegerField(verbose_name="工序库存")  # 生产线或车间内的库存
    material_inventory = models.IntegerField(verbose_name="资材库存")  # 总库存量

    def __str__(self):
        return f"{self.material_name} 库存"


# 主生产计划模型，用于定义每个物料的生产计划
class MPS(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    quantity = models.IntegerField(verbose_name="数量")
    date = models.DateField(verbose_name="日期")

    def __str__(self):
        return f"{self.material_code} - {self.quantity} - {self.date}"


# MPS 记录模型，定义生产计划的需求和到期日
class MPSRecord(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料编号")
    required_quantity = models.IntegerField(verbose_name="需求数量")
    due_date = models.DateField(verbose_name="需求日期")

    def __str__(self):
        return f"{self.material_code} - {self.required_quantity} on {self.due_date}"


# 采购计划模型，记录物料的采购需求
class PurchasePlan(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    quantity = models.IntegerField(verbose_name="采购数量")
    date = models.DateField(verbose_name="计划日期")


# 生产计划模型，记录物料的生产计划
class ProductionPlan(models.Model):
    material_code = models.CharField(max_length=10, verbose_name="物料号")
    quantity = models.IntegerField(verbose_name="生产数量")
    date = models.DateField(verbose_name="计划日期")
