from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.items, name='items'),

    path('login/', auth_views.LoginView.as_view(
        template_name='main/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('items/add/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.item_update, name='item_update'),
    path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('items/<int:pk>/pin/', views.item_toggle_pin, name='item_toggle_pin'),
    path('items/pin/reorder/', views.item_reorder, name='item_reorder'),
    path('filters/preferences/', views.filter_preferences, name='filter_preferences'),
    path('settings/', views.settings_view, name='settings'),
]
