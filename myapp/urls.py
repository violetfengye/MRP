from django.urls import path
from . import views

urlpatterns = [
    path('mrp/', views.mrp_calculation, name='mrp_calculation'),
    path("", views.index, name="index"),
    path("input_mps/", views.input_mps, name="input_mps"),
    path('create_mps/', views.create_mps_record, name='create_mps'),
    path('mps_success/', views.mps_success, name='mps_success'),
]
