from django.shortcuts import render, redirect, get_object_or_404 # Додав get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import UserRegisterForm
from django.http import JsonResponse

def index(request):
    featured_products = Product.objects.filter(available=True).order_by('-id')[:3]
    trending_products = Product.objects.filter(available=True)[:6]
    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
    }
    return render(request, 'shop/index.html', context)

def product_list(request):
    # --- ЛОГІКА ДОДАВАННЯ В КОШИК ---
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        
        # Додаємо 1 до кількості товару в сесії
        cart[product_id] = cart.get(product_id, 0) + 1
        
        request.session['cart'] = cart
        return redirect('shop:cart_detail') # Перекидаємо в кошик після кліку
    # --------------------------------

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

def index(request):
    featured_products = Product.objects.filter(available=True).order_by('-id')[:3]
    trending_products = Product.objects.filter(available=True)[:6]
    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
    }
    return render(request, 'shop/index.html', context)

def product_list(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart
        return redirect('shop:cart_detail')

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

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total,
            })
        except Product.DoesNotExist:
            continue

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/cart_detail.html', context)

# --- ОНОВЛЕНІ ФУНКЦІЇ ДЛЯ РОБОТИ БЕЗ ПЕРЕЗАВАНТАЖЕННЯ (AJAX) ---

def cart_add_one(request, product_id):
    cart = request.session.get('cart', {})
    str_id = str(product_id)
    
    if str_id in cart:
        cart[str_id] += 1
    else:
        cart[str_id] = 1
        
    request.session['cart'] = cart
    request.session.modified = True # Явно кажемо Django зберегти сесію

    # Розрахунок нових значень для відповіді скрипту
    product = get_object_or_404(Product, id=product_id)
    item_total = product.price * cart[str_id]
    
    # Рахуємо загальну суму кошика
    total_cart_price = sum(Product.objects.get(id=pid).price * qty 
                           for pid, qty in cart.items() if Product.objects.filter(id=pid).exists())

    return JsonResponse({
        'status': 'ok',
        'quantity': cart[str_id],
        'item_total': float(item_total),
        'total_cart_price': float(total_cart_price)
    })

def cart_remove_one(request, product_id):
    cart = request.session.get('cart', {})
    str_id = str(product_id)
    
    quantity = 0
    item_total = 0
    
    if str_id in cart:
        if cart[str_id] > 1:
            cart[str_id] -= 1
            quantity = cart[str_id]
            product = get_object_or_404(Product, id=product_id)
            item_total = product.price * quantity
        else:
            del cart[str_id]
            quantity = 0
            
    request.session['cart'] = cart
    request.session.modified = True

    total_cart_price = sum(Product.objects.get(id=pid).price * qty 
                           for pid, qty in cart.items() if Product.objects.filter(id=pid).exists())

    return JsonResponse({
        'status': 'ok',
        'quantity': quantity,
        'item_total': float(item_total),
        'total_cart_price': float(total_cart_price)
    })