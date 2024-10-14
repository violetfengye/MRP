from django.urls import path
from . import views

# 定义 URL 模式，映射到视图函数
urlpatterns = [
    path('', views.main_page, name='main_page'),  # 不带任何后缀进入主界面
    path('mps_input/', views.mps_input, name='mps_input'),  # 输入 MPS 页面
    path('mps_success', views.mps_success, name='mps_success'),  # MPS成功记录
    path('mrp_query/', views.mrp_query, name='mrp_query'),  # MRP查询计算
    path('mrp_results/<str:mps_ids>/', views.mrp_results, name='mrp_results'),  # MPR计算结果
    path('mps_display', views.mps_display, name='mps_display'),  # 查询mps记录
    path('delete_mps/<int:mps_id>/', views.delete_mps_record, name='delete_mps_record'),  # 删除mps记录
    path('inventories_display', views.inventories_display, name='inventories_display'),  # 查看仓库
    path('update_inventory/<str:inventory_id>/', views.update_inventory, name='update_inventory'),  # 更新仓库
    path('error/', views.error, name='error'),  # 错误界面
    # Add other paths as necessary
]
