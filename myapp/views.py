from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Inventory, BillOfMaterial, AllocationComposition, Material, ProductionPlan, PurchasePlan, MPS, \
    MPSRecord
from .forms import MPSForm, MPSRecordFormSet
from collections import defaultdict

def main_page(request):
    # Render the main page template with buttons
    return render(request, 'main_page.html')
def build_dependency_graph(boms):
    # 建立物料依赖图
    graph = defaultdict(list)
    for bom in boms:
        graph[bom.part_number].append((bom.part_number, bom.quantity))  # 使用 part_number 而不是 parent_material_code
    return graph



def topological_sort(graph):
    # 执行拓扑排序
    visited = set()
    stack = []

    def dfs(material_code):
        visited.add(material_code)
        for child, _ in graph[material_code]:
            if child not in visited:
                dfs(child)
        stack.append(material_code)

    for material in graph:
        if material not in visited:
            dfs(material)

    return stack[::-1]  # 反转为拓扑排序顺序


def calculate_material_requirements(topological_order, inventories, mps_records):
    # 计算物料需求
    requirements = {}
    memo = {}  # 记忆化缓存

    def compute_net_requirement(material_code):
        # 递归计算净需求量
        if material_code in memo:
            return memo[material_code]

        required_quantity = mps_records.get(material_code, {}).get('required_quantity', 0)
        stock_quantity = inventories.get(material_code, 0)
        net_requirement = max(required_quantity - stock_quantity, 0)

        memo[material_code] = net_requirement
        return net_requirement

    for material_code in topological_order:
        net_requirement = compute_net_requirement(material_code)
        requirements[material_code] = {
            'required_quantity': mps_records.get(material_code, {}).get('required_quantity', 0),
            'net_requirement': net_requirement,
            'allocation_lead_time': 0,  # 假设提前期
            'supplier_lead_time': 0,  # 假设提前期
            'due_date': None  # 可根据需求设置
        }

    return requirements


def mrp_calculation(request):
    # MRP 计算视图
    mps_records = MPS.objects.all()
    results = []
    boms = BillOfMaterial.objects.all()
    inventories = {inv.material_code: inv.workshop_inventory + inv.material_inventory for inv in
                   Inventory.objects.all()}  # 以物料编码为键存储库存

    graph = build_dependency_graph(boms)  # 构建物料依赖图
    topological_order = topological_sort(graph)  # 获取拓扑排序

    mps_data = {record.material_code: {'required_quantity': record.quantity} for record in mps_records}
    requirements = calculate_material_requirements(topological_order, inventories, mps_data)  # 计算物料需求

    for code, item in requirements.items():
        results.append({
            'material_code': code,
            'required_quantity': item['required_quantity'],
            'net_requirement': item['net_requirement'],
            'allocation_lead_time': item['allocation_lead_time'],
            'supplier_lead_time': item['supplier_lead_time'],
            'due_date': item['due_date'],
        })

    print("计算结果:", results)  # 输出计算结果到控制台
    return render(request, 'mrp_results.html', {'results': results})  # 渲染结果到模板


def mps_success(request):
    # MPS 成功页面视图
    mps_records = MPSRecord.objects.all()
    procurement_plan, production_plan = generate_plans(mps_records)  # 生成采购和生产计划
    return render(request, 'mps_success.html', {
        'procurement_plan': procurement_plan,
        'production_plan': production_plan
    })


def input_mps(request):
    # 输入 MPS 记录的视图
    if request.method == "POST":
        form = MPSForm(request.POST)
        if form.is_valid():
            form.save()  # 保存有效的 MPS 记录
            return redirect('input_mps')  # 重定向到输入 MPS 页面
    else:
        form = MPSForm()  # 初始化表单

    return render(request, 'input_mps.html', {'form': form})  # 渲染输入页面


def create_mps_record(request):
    # 创建 MPS 记录的视图
    if request.method == 'POST':
        form = MPSForm(request.POST)
        if form.is_valid():
            form.save()  # 保存 MPS 记录
            return redirect('mps_success')  # 重定向到成功页面
    else:
        form = MPSForm()  # 初始化表单

    return render(request, 'create_mps.html', {'form': form})  # 渲染创建页面


def mps_input(request):
    # 批量输入 MPS 记录的视图
    if request.method == 'POST':
        formset = MPSRecordFormSet(request.POST)
        if formset.is_valid():
            mps_records = formset.save()  # 保存有效的表单集
            generate_plans(mps_records)  # 生成采购和生产计划
            return redirect('mps_success')  # 重定向到成功页面
    else:
        formset = MPSRecordFormSet()  # 初始化表单集

    return render(request, 'mps_input.html', {'formset': formset})  # 渲染输入页面


def generate_plans(mps_records):
    # 生成采购和生产计划
    procurement_plan = []
    production_plan = []

    for record in mps_records:
        material = Material.objects.get(material_code=record.material_code)
        required_quantity = record.required_quantity

        if material.stock < required_quantity:
            # 库存不足，生成采购计划
            procurement_quantity = required_quantity - material.stock
            procurement_plan.append({
                'material_code': material.material_code,
                'procurement_quantity': procurement_quantity
            })
            # 保存到采购计划表
            PurchasePlan.objects.create(
                material_code=material.material_code,
                quantity=procurement_quantity,
                date=record.date
            )
        else:
            # 库存足够，生成生产计划
            production_plan.append({
                'material_code': material.material_code,
                'production_quantity': required_quantity
            })
            # 保存到生产计划表
            ProductionPlan.objects.create(
                material_code=material.material_code,
                quantity=required_quantity,
                date=record.date
            )

    return procurement_plan, production_plan  # 返回采购和生产计划
