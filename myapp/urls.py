from django.urls import path
from . import views

# 定义 URL 模式，映射到视图函数
urlpatterns = [
    path('', views.main_page, name='main_page'),  # 不带任何后缀进入主界面
    path('mps_input/', views.mps_input, name='mps_input'),  # 输入 MPS 页面
    path('mps_success', views.mps_success, name='mps_success'),
    path('mrp_query/', views.mrp_query, name='mrp_query'),  # For MRP Query
    path('mrp_results/<str:mps_ids>/', views.mrp_results, name='mrp_results'),
    path('mps_display', views.mps_display, name='mps_display'),
    path('delete_mps/<int:mps_id>/', views.delete_mps_record, name='delete_mps_record'),

    # Add other paths as necessary
]
