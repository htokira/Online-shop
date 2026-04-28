from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product, Category, OrderItem  # Об'єднали моделі
from .forms import UserRegisterForm, OrderCreateForm  # Об'єднали форми
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

def order_create(request):
    cart = request.session.get('cart', {})
    
    # Якщо кошик порожній, не даємо оформлювати замовлення
    if not cart:
        return redirect('shop:product_list')

    # Підготовка даних для відображення в правій частині (чекаут)
    cart_items = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': item_total
        })

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 1. Створюємо замовлення
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            # 2. Переносимо товари з кошика в OrderItem
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity']
                )
            
            # 3. Очищаємо кошик
            request.session['cart'] = {}
            
            # 4. Сторінка успіху
            return render(request, 'shop/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
    
    # Передаємо cart_items та total_price, щоб шаблон їх побачив
    return render(request, 'shop/order_create_form.html', {
        'cart_items': cart_items, 
        'total_price': total_price, 
        'form': form
    })

def cart_detail(request):
    cart = request.session.get('cart', {})
    # Логіка відображення кошика
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0
    for product in products:
        quantity = cart.get(str(product.id))
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': item_total,
        })

    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * cart[product_id_str]
        total_cart_price = sum(Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items())
        return JsonResponse({
            'status': 'ok',
            'quantity': cart[product_id_str],
            'item_total': float(item_total),
            'total_cart_price': float(total_cart_price)
        })
    
    return redirect('shop:cart_detail')

def cart_remove_one(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if cart[product_id_str] > 1:
            cart[product_id_str] -= 1
        else:
            del cart[product_id_str]
            
    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        quantity = cart.get(product_id_str, 0)
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total_cart_price = sum(Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items())
        return JsonResponse({
            'status': 'ok',
            'quantity': quantity,
            'item_total': float(item_total),
            'total_cart_price': float(total_cart_price)
        })

    return redirect('shop:cart_detail')
def cart_remove_all(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        
    request.session['cart'] = cart
    request.session.modified = True
    
    # Додаємо підтримку AJAX для повного видалення рядка
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_cart_price = sum(Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items())
        return JsonResponse({
            'status': 'ok',
            'quantity': 0,
            'item_total': 0,
            'total_cart_price': float(total_cart_price)
        })

    return redirect('shop:cart_detail')