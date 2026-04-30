from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail')
]