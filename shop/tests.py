from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Profile, Order, OrderItem

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Подушки")
        self.product = Product.objects.create(
            category=self.category,
            name="Ортопедична подушка",
            price=500.00,
            available=True
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Ортопедична подушка")
        self.assertEqual(self.product.price, 500.00)

    def test_product_update(self):
        self.product.name = "Оновлене ім'я"
        self.product.price = 550.00
        self.product.available = False
        self.product.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Оновлене ім'я")
        self.assertEqual(self.product.price, 550.00)
        self.assertEqual(self.product.available, False)

    def test_product_delete(self):
        self.product.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(name = "Ортопедична подушка")

class ShopViewsTest(TestCase):
    def test_homepage_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'shop/index.html')

class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        Profile.objects.create(user=self.user, phone_number='+380991112233')
    
    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_successful(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_failed(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'WrongPassword!'
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_registration_successful(self):
        response = self.client.post(reverse('shop:register'), {
            'username': 'new_user',
            'email': 'new@example.com',
            'phone_number': '+380991234567',
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username='new_user').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.profile.phone_number, '+380991234567')

class ProductListViewTest(TestCase):
    
    def setUp(self):

        self.category1 = Category.objects.create(name="Подушки")
        self.category2 = Category.objects.create(name="Аксесуари для подушок")

        self.product1 = Product.objects.create(
            category=self.category1, name="Ортопедична подушка", price=3000, available=True)
        self.product2 = Product.objects.create(
            category=self.category1, name="Квадратна подушка", price=1500, available=True)
        self.product3 = Product.objects.create(
            category=self.category1, name="Еко-подушка", price=4000, available=True)
        self.product4 = Product.objects.create(
            category=self.category2, name="Шовкова наволочка", price=5000, available=True)
        
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_search_by_name(self):
        response = self.client.get(reverse('shop:product_list') + '?q=Ортопед')
        products = response.context['products'] 
        
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Ортопедична подушка")

    def test_filter_by_category(self):
        response = self.client.get(reverse('shop:product_list') + f'?category={self.category1.id}')
        products = response.context['products']
        
        self.assertEqual(len(products), 3) 
        self.assertNotIn(self.product4, products)

    def test_sorting_by_price_desc(self):
        response = self.client.get(reverse('shop:product_list') + '?sort=price_desc')
        
        products = list(response.context['products']) 
        
        self.assertEqual(products[0].name, "Шовкова наволочка")
        self.assertEqual(products[1].name, "Еко-подушка")
        self.assertEqual(products[2].name, "Ортопедична подушка")
        self.assertEqual(products[3].name, "Квадратна подушка")
    
    def test_sorting_by_price_asc(self):
        response = self.client.get(reverse('shop:product_list') + '?sort=price_asc')
        products = list(response.context['products']) 
        
        self.assertEqual(products[0].name, "Квадратна подушка")
        self.assertEqual(products[1].name, "Ортопедична подушка")
        self.assertEqual(products[2].name, "Еко-подушка")
        self.assertEqual(products[3].name, "Шовкова наволочка")

    def test_search_no_results(self):
        response = self.client.get(reverse('shop:product_list') + '?q=NoneFound')
        products = response.context['products'] 
        
        self.assertEqual(len(products), 0)
        self.assertContains(response, "No products found")

class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            category=self.category, 
            name="Товар", 
            price=100.00, 
            available=True,
            stock=10
        )

    def test_add_to_cart(self):
        """Тест додавання товару (використовуємо правильне ім'я cart_add_one)"""
        # Використовуємо 'shop:cart_add_one' згідно з твоїм urls.py
        response = self.client.post(reverse('shop:cart_add_one', args=[self.product.id]))
        self.assertEqual(response.status_code, 302) 
        self.assertIn(str(self.product.id), self.client.session['cart'])

    def test_cart_total_price(self):
        """Тест підрахунку вартості (використовуємо число 2 замість словника)"""
        session = self.client.session
        session['cart'] = {str(self.product.id): 2} # Передаємо просто число
        session.save()
        
        response = self.client.get(reverse('shop:cart_detail'))
        self.assertEqual(response.status_code, 200)
        # Перевіряємо, чи в контексті є об'єкт cart і чи вірна сума
        self.assertEqual(response.context['total_price'], 200.00)


class OrderCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='password123')
        self.user.first_name = "Марія"
        self.user.save()
        Profile.objects.create(user=self.user, phone_number='+380501112233')
        
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            category=self.category, name="Товар", price=100, available=True, stock=10
        )

    def test_order_form_initial_data(self):
        """Тест автозаповнення форми"""
        # 1. Логінимо користувача
        self.client.login(username='buyer', password='password123')
        
        # 2. Наповнюємо кошик (числом)
        session = self.client.session
        session['cart'] = {str(self.product.id): 1}
        session.save()

        # 3. Робимо запит на сторінку
        response = self.client.get(reverse('shop:order_create'))
        
        # Перевіряємо, чи юзер справді авторизований у цьому запиті
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Перевіряємо значення у формі. 
        # Якщо first_name знову видасть KeyError, спробуй перевірити 'email' або 'phone'
        form = response.context['form']
        self.assertEqual(form.initial.get('first_name'), "Марія")
        self.assertEqual(form.initial.get('phone'), "+380501112233")

    def test_order_creation_clears_cart(self):
        """Тест створення замовлення"""
        self.client.login(username='buyer', password='password123')
        session = self.client.session
        session['cart'] = {str(self.product.id): 1}
        session.save()

        order_data = {
            'first_name': 'Марія',
            'last_name': 'Тестова',
            'email': 'maria@example.com',
            'phone': '+380501112233',
            'address': 'Київ'
        }
        
        response = self.client.post(reverse('shop:order_create'), data=order_data)
        self.assertEqual(Order.objects.count(), 1)
        # Після замовлення кошик у сесії має стати порожнім словником
        self.assertEqual(self.client.session['cart'], {})