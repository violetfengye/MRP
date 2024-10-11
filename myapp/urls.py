from django.urls import path
from . import views

# 定义 URL 模式，映射到视图函数
urlpatterns = [
    path('mrp/', views.mrp_calculation, name='mrp_calculation'),  # MRP 计算页面  # 主页
    path("input_mps/", views.input_mps, name="input_mps"),  # 输入 MPS 页面
    path('create_mps/', views.create_mps_record, name='create_mps'),  # 创建 MPS 记录的页面
    path('mps_success/', views.mps_success, name='mps_success'),  # MPS 创建成功后跳转页面
    path('', views.main_page, name='main_page'),  # Main page view
    path('mps_input/', views.mps_input, name='mps_input'),  # MPS input view
    path('mps_calculation/', views.mrp_calculation, name='mrp_calculation'),  # MRP calculation view
    # Add other paths as necessary
]
