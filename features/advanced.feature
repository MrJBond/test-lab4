Feature: Advanced testing for E-Shop (Edge cases, types, boundaries)
  We want to test edge cases, incorrect types, and boundaries for Product, ShoppingCart, and Order.

  # 1. Погранична поведінка: запит точної кількості, що є в наявності
  Scenario: Check availability on the exact boundary
    Given A product "Laptop" with price 1000 and availability 5
    When I check if "Laptop" is available in amount 5
    Then The product should be available

  # 2. Погранична поведінка: запит на 1 більше, ніж є в наявності
  Scenario: Check availability just above the boundary
    Given A product "Laptop" with price 1000 and availability 5
    When I check if "Laptop" is available in amount 6
    Then The product should not be available

  # 3. Неправильний тип даних: передача None замість об'єкта
  Scenario: Add None as a product to the cart
    Given An empty shopping cart
    When I add None to the cart
    Then An exception should be raised

  # 4. Неправильний тип даних: передача рядка замість числа у кількість
  Scenario: Add product with invalid amount type (string)
    Given A product "Mouse" with price 50 and availability 10
    And An empty shopping cart
    When I add "Mouse" to the cart with string amount "five"
    Then A TypeError should be raised

  # 5. Стан системи: розрахунок пустої корзини
  Scenario: Calculate total for an empty cart
    Given An empty shopping cart
    When I calculate the total price
    Then The total price should be 0

  # 6. Стан системи: розрахунок корзини з кількома товарами
  Scenario: Calculate total with multiple products
    Given An empty shopping cart
    And A product "Keyboard" with price 100 and availability 10
    And A product "Mouse" with price 50 and availability 10
    When I add "Keyboard" to the cart in amount 2
    And I add "Mouse" to the cart in amount 1
    And I calculate the total price
    Then The total price should be 250

  # 7. Базовий функціонал: видалення товару
  Scenario: Remove an existing product from the cart
    Given An empty shopping cart
    And A product "Monitor" with price 300 and availability 5
    And I add "Monitor" to the cart in amount 1
    When I remove "Monitor" from the cart
    Then The cart should not contain "Monitor"

  # 8. Погранична поведінка: видалення товару, якого немає в корзині
  Scenario: Remove a non-existent product from the cart
    Given An empty shopping cart
    And A product "Desk" with price 200 and availability 2
    When I remove "Desk" from the cart
    Then The cart should remain empty without errors

  # 9. Інтеграція: успішне створення замовлення
  Scenario: Successfully place an order
    Given An empty shopping cart
    And A product "Pen" with price 5 and availability 100
    And I add "Pen" to the cart in amount 10
    And An order is created from the cart
    When I place the order
    Then The cart should be empty
    And The product "Pen" availability should be 90

  # 10. Інтеграція: створення замовлення з пустою корзиною
  Scenario: Place an order with an empty cart
    Given An empty shopping cart
    And An order is created from the cart
    When I place the order
    Then The cart should be empty