from behave import given, when, then
from app.eshop import Product, ShoppingCart, Order

@given('A product "{name}" with price {price:d} and availability {availability:d}')
def step_impl(context, name, price, availability):
    if not hasattr(context, 'products'):
        context.products = {}
    context.products[name] = Product(name=name, price=price, available_amount=availability)

@when('I check if "{name}" is available in amount {amount:d}')
def step_impl(context, name, amount):
    context.is_available = context.products[name].is_available(amount)

@then('The product should be available')
def step_impl(context):
    assert context.is_available is True

@then('The product should not be available')
def step_impl(context):
    assert context.is_available is False

@when('I add None to the cart')
def step_impl(context):
    context.exception_raised = False
    try:
        context.cart.add_product(None, 1)
    except Exception:
        context.exception_raised = True

@then('An exception should be raised')
def step_impl(context):
    assert context.exception_raised is True

@when('I add "{name}" to the cart with string amount "{amount}"')
def step_impl(context, name, amount):
    context.type_error_raised = False
    try:
        context.cart.add_product(context.products[name], amount)
    except TypeError:
        context.type_error_raised = True

@then('A TypeError should be raised')
def step_impl(context):
    assert context.type_error_raised is True

@when('I calculate the total price')
def step_impl(context):
    context.total_price = context.cart.calculate_total()

@then('The total price should be {expected_total:d}')
def step_impl(context, expected_total):
    assert context.total_price == expected_total

@when('I add "{name}" to the cart in amount {amount:d}')
@given('I add "{name}" to the cart in amount {amount:d}')
def step_impl(context, name, amount):
    context.cart.add_product(context.products[name], amount)

@when('I remove "{name}" from the cart')
def step_impl(context, name):
    context.cart.remove_product(context.products[name])

@then('The cart should not contain "{name}"')
def step_impl(context, name):
    assert context.cart.contains_product(context.products[name]) is False

@then('The cart should remain empty without errors')
def step_impl(context):
    assert len(context.cart.products) == 0

@given('An order is created from the cart')
def step_impl(context):
    context.order = Order(context.cart)

@when('I place the order')
def step_impl(context):
    context.order.place_order()

@then('The cart should be empty')
def step_impl(context):
    assert len(context.cart.products) == 0

@then('The product "{name}" availability should be {expected_amount:d}')
def step_impl(context, name, expected_amount):
    assert context.products[name].available_amount == expected_amount