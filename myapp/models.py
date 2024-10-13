from django.db import models


# BOM模型
class BillOfMaterial(models.Model):
    material_id = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="物料号", to_field='material_id',
                                    related_name="boms")
    description = models.CharField(max_length=50, verbose_name="描述")
    quantity = models.IntegerField(verbose_name="装配数量")
    unit = models.CharField(max_length=2, verbose_name="单位")
    level = models.IntegerField(verbose_name="层次")

    class Meta:
        unique_together = ('description', 'level')  # 添加唯一约束

    def __str__(self):
        return f"BOM: {self.description} - {self.material_id} - {self.quantity} {self.unit}"


# 物料模型
class Material(models.Model):
    material_id = models.CharField(max_length=10, verbose_name="物料号", unique=True)
    name = models.CharField(max_length=20, primary_key=True, verbose_name="名称")
    unit = models.CharField(max_length=5, verbose_name="单位")
    allocation_method = models.CharField(max_length=10, verbose_name="调配方式")
    loss_rate = models.FloatField(verbose_name="损耗率")
    lead_time = models.IntegerField(verbose_name="作业提前期")

    def __str__(self):
        return f"Material: {self.name} ({self.material_id})"


# 配料组成模型
class AllocationComposition(models.Model):
    base_code = models.CharField(max_length=10, verbose_name="调配基准编号")
    region_code = models.CharField(max_length=10, verbose_name="调配区域代码")
    parent_material_code = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="父物料号",
                                             to_field='material_id', related_name="parent_compositions")
    parent_material_name = models.CharField(max_length=20, verbose_name="父物料名称")
    child_material_code = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="子物料号",
                                            to_field='material_id', related_name="child_compositions")
    child_material_name = models.CharField(max_length=20, verbose_name="子物料名称")
    quantity = models.IntegerField(verbose_name="构成数量")
    allocation_lead_time = models.IntegerField(verbose_name="配料提前期")
    supplier_lead_time = models.IntegerField(verbose_name="供应商提前期")

    class Meta:
        unique_together = ('parent_material_name', 'child_material_name')  # 复合唯一约束

    def __str__(self):
        return f"Allocation: {self.parent_material_name} -> {self.child_material_name} ({self.quantity})"


# 库存模型
class Inventory(models.Model):
    material_code = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="物料号",
                                      to_field='material_id', related_name="inventory")
    material_name = models.CharField(max_length=20, primary_key=True, verbose_name="物料名称")
    workshop_inventory = models.IntegerField(verbose_name="工序库存")
    material_inventory = models.IntegerField(verbose_name="资材库存")

    def __str__(self):
        return f"Inventory: {self.material_name} - Workshop: {self.workshop_inventory}, Material: {self.material_inventory}"


# MPS 记录模型
class MPSRecord(models.Model):
    mps_id = models.CharField(max_length=10, verbose_name="MPS编号", unique=True)
    material_name = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="产品名称", to_field='name',
                                      related_name="mps_records")
    required_quantity = models.IntegerField(verbose_name="需求数量")
    due_date = models.DateField(verbose_name="完工日期")

    def __str__(self):
        return f"MPS: {self.mps_id} - {self.material_name} - {self.due_date}"


# 采购计划模型
class PurchasePlan(models.Model):
    material_code = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="物料号",
                                      to_field='material_id', related_name="purchase_plans")
    name = models.CharField(max_length=10, primary_key=True, verbose_name="物料名称")
    quantity = models.IntegerField(verbose_name="采购数量")
    date = models.DateField(verbose_name="计划日期")

    def __str__(self):
        return f"Purchase Plan: {self.name} - {self.quantity} on {self.date}"


# 生产计划模型
class ProductionPlan(models.Model):
    material_code = models.ForeignKey('Material', on_delete=models.CASCADE, verbose_name="物料号",
                                      to_field='material_id', related_name="production_plans")
    name = models.CharField(max_length=10, primary_key=True, verbose_name="物料名称")
    quantity = models.IntegerField(verbose_name="生产数量")
    date = models.DateField(verbose_name="计划日期")

    def __str__(self):
        return f"Production Plan: {self.name} - {self.quantity} on {self.date}"
