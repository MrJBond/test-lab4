from behave import given, when, then
from eshop import Product

@given('The product with name "{name}" has availability of "{availability}"')
def step_impl(context, name, availability):
    # Ціна тут не має значення для перевірки наявності, тому ставимо довільну (наприклад, 100)
    context.product = Product(name=name, price=100, available_amount=int(availability))

@when('I check if product is available in amount "{amount}"')
def step_impl(context, amount):
    context.is_available = context.product.is_available(int(amount))

@then('Product is available')
def step_impl(context):
    assert context.is_available is True

@then('Product is not available')
def step_impl(context):
    assert context.is_available is False