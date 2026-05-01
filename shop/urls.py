from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('order/create/', views.order_create, name='order_create'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('about/', views.about, name='about'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile_settings', views.profile_settings, name='profile_settings'),
    
    # Ось ці три рядки врятують ситуацію:
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add_one'), # Зверни увагу на name
    path('cart/remove/<int:product_id>/', views.cart_remove_one, name='cart_remove_one'),
    path('cart/delete/<int:product_id>/', views.cart_remove_all, name='cart_remove_all'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('order/<int:order_id>/confirm/', views.confirm_order_receipt, name='confirm_order'),
]