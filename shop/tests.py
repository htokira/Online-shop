from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product

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
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        
        user_exists = User.objects.filter(username='new_user').exists()
        self.assertTrue(user_exists)
