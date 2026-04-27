from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('cart/', views.cart_detail, name='cart_detail'), # Твій кошик
    path('cart/add-one/<int:product_id>/', views.cart_add_one, name='cart_add_one'),
    path('cart/remove-one/<int:product_id>/', views.cart_remove_one, name='cart_remove_one'),
]