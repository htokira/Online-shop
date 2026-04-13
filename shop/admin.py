from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'image', 'available']
    list_filter = ['available', 'category']
    list_editable = ['price', 'stock', 'available'] 
    search_fields = ['name', 'description']

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']
    inlines = [CartItemInline] 

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'paid', 'created']
    list_filter = ['paid', 'created']
    search_fields = ['first_name', 'last_name', 'address']
    inlines = [OrderItemInline]
