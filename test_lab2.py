import unittest
from unittest.mock import MagicMock
from app.eshop import Product, ShoppingCart, Order

class TestEShop(unittest.TestCase):

    # --- Частина з методички (Лістинг 1) ---
    def setUp(self):
        # Створення тестових даних перед кожним тестом
        self.product = Product(name='Test Product', price=100.0, available_amount=10)
        self.cart = ShoppingCart()

    def tearDown(self):
        # Очищення після кожного тесту
        self.cart = ShoppingCart()

    def test_mock_add_product(self):
        """Тест з методички: перевірка виклику методу за допомогою Mock"""
        # Замінюємо реальний метод is_available на Mock-об'єкт
        self.product.is_available = MagicMock(return_value=True)

        self.cart.add_product(self.product, 5)

        # Перевіряємо, чи викликався метод is_available з аргументом 5
        self.product.is_available.assert_called_with(5)

    def test_add_available_amount(self):
        """Тест з методички: успішне додавання товару"""
        self.cart.add_product(self.product, 5)
        self.assertTrue(self.cart.contains_product(self.product),
                        'Продукт має бути успішно доданий до корзини')

    def test_add_non_available_amount(self):
        """Тест з методички: спроба додати більше, ніж є"""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 20)  # доступно лише 10
        self.assertFalse(self.cart.contains_product(self.product),
                         'Продукт не повинен бути доданий до корзини')

    # --- 10 Додаткових тестів (Завдання 3) ---

    # 1. Тестування рядкового представлення продукту
    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product',
                         "Метод __str__ має повертати ім'я продукту")

    # 2. Тестування зменшення кількості товару (метод buy)
    def test_product_buy(self):
        self.product.buy(3)
        self.assertEqual(self.product.available_amount, 7,
                         "Кількість товару має зменшитися на 3")

    # 3. Тестування розрахунку вартості пустої корзини
    def test_empty_cart_total(self):
        total = self.cart.calculate_total()
        self.assertEqual(total, 0.0, "Вартість пустої корзини має бути 0")

    # 4. Тестування розрахунку вартості корзини з кількома товарами
    def test_cart_total_calculation(self):
        prod2 = Product("Mouse", 50.0, 10)
        self.cart.add_product(self.product, 2)  # 100 * 2 = 200
        self.cart.add_product(prod2, 1)  # 50 * 1 = 50

        total = self.cart.calculate_total()
        self.assertEqual(total, 250.0, "Загальна сума має бути 250.0")

    # 5. Тестування видалення товару з корзини
    def test_remove_product(self):
        self.cart.add_product(self.product, 1)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product),
                         "Товар має бути видалений з корзини")

    # 6. Тестування видалення неіснуючого товару (не має викликати помилку)
    def test_remove_non_existent_product(self):
        try:
            self.cart.remove_product(self.product)
        except KeyError:
            self.fail("remove_product викликав помилку при видаленні відсутнього товару")

    # 7. Тестування граничного значення (додавання всієї наявної кількості)
    def test_add_exact_available_amount(self):
        self.cart.add_product(self.product, 10)  # доступно рівно 10
        self.assertTrue(self.cart.contains_product(self.product))

    # 8. Тестування класу Order (успішне замовлення)
    def test_order_success(self):
        self.cart.add_product(self.product, 5)

        # Створюємо заглушку для shipping_service
        mock_shipping = MagicMock()
        order = Order(self.cart, mock_shipping)

        # Тепер place_order вимагає тип доставки, передаємо будь-який
        order.place_order("Нова Пошта")

        # Перевіряємо, чи зменшилась кількість товару на складі
        self.assertEqual(self.product.available_amount, 5,
                         "Після замовлення кількість товару має зменшитись")

    # 9. Тестування очищення корзини після замовлення
    def test_cart_cleared_after_order(self):
        self.cart.add_product(self.product, 1)

        # Створюємо заглушку для shipping_service
        mock_shipping = MagicMock()
        order = Order(self.cart, mock_shipping)
        order.place_order("Нова Пошта")

        self.assertEqual(len(self.cart.products), 0, "Корзина має бути пуста після замовлення")

    # 10. Тестування нерівності продуктів (різні імена)
    def test_product_inequality(self):
        prod2 = Product("Other Product", 100.0, 10)
        self.assertNotEqual(self.product, prod2, "Продукти з різними іменами не мають бути рівні")


if __name__ == '__main__':
    unittest.main()