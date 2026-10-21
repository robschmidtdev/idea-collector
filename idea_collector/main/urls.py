from django.urls import path
from . import views

urlpatterns = [
    path('', views.items, name='items'),

    path('items/add/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('settings/', views.settings_view, name='settings'),
]
