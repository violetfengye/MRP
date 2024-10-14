from django.contrib import admin
from .models import BillOfMaterial, Material, AllocationComposition, Inventory, MPSRecord, BalanceSheet


# 注册 BOM 模型
@admin.register(BillOfMaterial)
class BillOfMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'description', 'quantity', 'unit', 'level')
    search_fields = ('description', 'material_id__material_id')
    list_filter = ('level',)


# 注册 Material 模型
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'name', 'unit', 'allocation_method', 'loss_rate', 'lead_time')
    search_fields = ('name', 'material_id')


# 注册 AllocationComposition 模型
@admin.register(AllocationComposition)
class AllocationCompositionAdmin(admin.ModelAdmin):
    list_display = (
        'parent_material_name', 'child_material_name', 'quantity', 'allocation_lead_time', 'supplier_lead_time')
    search_fields = ('parent_material_name', 'child_material_name')


# 注册 Inventory 模型
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('material_name', 'workshop_inventory', 'material_inventory')
    search_fields = ('material_name',)


# 注册 MPSRecord 模型
@admin.register(MPSRecord)
class MPSRecordAdmin(admin.ModelAdmin):
    list_display = ('mps_id', 'material_name', 'required_quantity', 'due_date')
    search_fields = ('mps_id', 'material_name__name')


# 注册 BalanceSheet 模型
@admin.register(BalanceSheet)
class BalanceSheetAdmin(admin.ModelAdmin):
    list_display = ('bs_id', 'bs_toid', 'bs_var')
    search_fields = ('bs_var',)
