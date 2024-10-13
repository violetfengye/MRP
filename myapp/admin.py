from django.contrib import admin
from .models import BillOfMaterial, Material, AllocationComposition, Inventory

# 注册模型到 Django 管理后台
@admin.register(BillOfMaterial)
class BillOfMaterialAdmin(admin.ModelAdmin):
    # 使用模型中存在的字段
    list_display = ('material_id', 'description', 'quantity', 'unit', 'level')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    # 使用模型中存在的字段
    list_display = ('material_id', 'name', 'unit', 'allocation_method', 'loss_rate', 'lead_time')


@admin.register(AllocationComposition)
class AllocationCompositionAdmin(admin.ModelAdmin):
    list_display = (
        'base_code', 'region_code',
        'parent_material_code', 'parent_material_name',
        'child_material_code', 'child_material_name',
        'quantity', 'allocation_lead_time', 'supplier_lead_time'
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # 使用模型中存在的字段
    list_display = ('material_code', 'material_name', 'workshop_inventory', 'material_inventory')
