from django.test import TestCase
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

    
