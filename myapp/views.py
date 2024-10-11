from django.shortcuts import render
from django.http import HttpResponse
from .models import Inventory, BillOfMaterial, AllocationComposition, Material, ProductionPlan, PurchasePlan


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def mrp_calculation(request):
    # 获取所有的 MPS 记录
    mps_records = MPS.objects.all()

    # 准备存放计算结果的列表
    results = []

    # 获取所有 BOM 和库存数据
    boms = BillOfMaterial.objects.all()
    inventories = Inventory.objects.all()
    allocations = AllocationComposition.objects.all()

    # 遍历每一个 MPS 记录
    for mps_record in mps_records:
        parent_material = mps_record.material_code
        required_quantity = mps_record.quantity

        # 计算净需求量
        parent_inventory = inventories.filter(material_code=parent_material).first()
        if parent_inventory:
            net_requirement = max(
                required_quantity - parent_inventory.workshop_inventory - parent_inventory.material_inventory, 0)
        else:
            net_requirement = required_quantity  # 如果没有库存，假设全为净需求

        # 记录父物料计算结果
        results.append({
            'material_code': parent_material,
            'required_quantity': required_quantity,
            'net_requirement': net_requirement,
            'allocation_lead_time': None,  # 父物料不需要配料提前期
            'supplier_lead_time': None,  # 父物料不需要供应商提前期
            'due_date': mps_record.date,  # 需求日期
        })

        # 查找子物料
        child_boms = boms.filter(part_number=parent_material)  # 这里用 part_number 查找子物料
        for child_bom in child_boms:
            child_inventory = inventories.filter(material_code=child_bom.part_number).first()
            allocation = allocations.filter(parent_material_code=parent_material,
                                            child_material_code=child_bom.part_number).first()

            # 计算子物料的净需求量
            if child_inventory:
                child_required_quantity = net_requirement * child_bom.quantity
                child_net_requirement = max(
                    child_required_quantity - child_inventory.workshop_inventory - child_inventory.material_inventory,
                    0)
            else:
                child_net_requirement = net_requirement * child_bom.quantity

            # 获取配料提前期和供应商提前期，如果没有找到 allocation，默认值为0
            allocation_lead_time = 0
            supplier_lead_time = 0
            if allocation:
                allocation_lead_time = allocation.allocation_lead_time
                supplier_lead_time = allocation.supplier_lead_time

            # 记录子物料的计算结果
            results.append({
                'material_code': child_bom.part_number,
                'required_quantity': child_required_quantity,
                'net_requirement': child_net_requirement,
                'allocation_lead_time': allocation_lead_time,
                'supplier_lead_time': supplier_lead_time,
                'due_date': mps_record.date,  # 将需求日期传递给子物料
            })

    # 调试输出，打印计算结果到控制台
    print("计算结果:", results)  # 输出计算结果到控制台

    # 渲染结果到模板
    return render(request, 'mrp_results.html', {'results': results})


from django.shortcuts import render, redirect
from .forms import MPSForm, MPSRecordFormSet
from .models import MPS


def mps_success(request):
    # 获取最近保存的 MPS 记录
    mps_records = MPSRecord.objects.all()

    # 生成采购和生产计划
    procurement_plan, production_plan = generate_plans(mps_records)

    return render(request, 'mps_success.html', {
        'procurement_plan': procurement_plan,
        'production_plan': production_plan
    })


def input_mps(request):
    if request.method == "POST":
        form = MPSForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('input_mps')  # 可以重定向到显示所有 MPS 的页面
    else:
        form = MPSForm()
    return render(request, 'input_mps.html', {'form': form})


def create_mps_record(request):
    if request.method == 'POST':
        form = MPSForm(request.POST)
        if form.is_valid():
            form.save()  # 保存 MPS 记录
            return redirect('mps_success')  # 重定向到成功页面或其他页面
    else:
        form = MPSForm()

    return render(request, 'create_mps.html', {'form': form})


from django.shortcuts import render, redirect
from .models import MPSRecord  # 假设已经有MPSRecord表单


def mps_input(request):
    if request.method == 'POST':
        formset = MPSRecordFormSet(request.POST)
        if formset.is_valid():
            mps_records = formset.save()
            # 生成采购和生产计划
            generate_plans(mps_records)
            return redirect('mps_success')
    else:
        formset = MPSRecordFormSet()

    return render(request, 'mps_input.html', {'formset': formset})


def generate_plans(mps_records):
    # 初始化采购和生产计划
    procurement_plan = []
    production_plan = []

    # 遍历所有 MPS 记录
    for record in mps_records:
        # 获取物料信息
        material = Material.objects.get(material_code=record.material_code)
        required_quantity = record.required_quantity

        # 根据库存和需求生成采购和生产计划
        if material.stock < required_quantity:
            procurement_quantity = required_quantity - material.stock
            procurement_plan.append({
                'material_code': material.material_code,
                'procurement_quantity': procurement_quantity
            })
            # 保存到采购计划表
            PurchasePlan.objects.create(
                material_code=material.material_code,
                procurement_quantity=procurement_quantity,
                planned_date=record.date
            )
        else:
            production_plan.append({
                'material_code': material.material_code,
                'production_quantity': required_quantity
            })
            # 保存到生产计划表
            ProductionPlan.objects.create(
                material_code=material.material_code,
                production_quantity=required_quantity,
                planned_date=record.date
            )

    return procurement_plan, production_plan



