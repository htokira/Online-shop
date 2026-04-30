from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import UserRegisterForm

def index(request):
    featured_products = Product.objects.filter(available=True).order_by('-id')[:3]
    trending_products = Product.objects.filter(available=True)[:6]

    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
    }
    
    return render(request, 'shop/index.html', context)

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_id:
        products = products.filter(category_id=category_id)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_id,
        'current_sort': sort_by,
    }
    
    return render(request, 'shop/product_list.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) 
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:product_list')
    else:
        form = UserRegisterForm()
        
    return render(request, 'registration/register.html', {'form': form})

@login_required 
def profile(request):
    return render(request, 'shop/profile.html')

def product_detail(request, product_id):
    # Шукаємо товар за ID, або видаємо помилку 404, якщо такого немає
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/single_product.html', {'product': product})