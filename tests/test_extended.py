import pytest
import uuid
import boto3
from datetime import datetime, timedelta, timezone
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE, SHIPPING_TABLE_NAME


# Фікстура для створення сервісу з реальними (не mock) залежностями
@pytest.fixture
def real_shipping_service():
    repo = ShippingRepository()
    pub = ShippingPublisher()
    return ShippingService(repo, pub)


# 1. Тест: Перевірка запису в DynamoDB (Bottom-Up: тестуємо репозиторій)
def test_repository_creates_item_in_db(dynamo_resource):
    repo = ShippingRepository()
    order_id = str(uuid.uuid4())
    due_date = datetime.now() + timedelta(days=1)

    shipping_id = repo.create_shipping("Nova Poshta", ["prod1"], order_id, "created", due_date)

    # Direct DB check
    table = dynamo_resource.Table(SHIPPING_TABLE_NAME)
    item = table.get_item(Key={'shipping_id': shipping_id})['Item']

    assert item['order_id'] == order_id
    assert item['shipping_status'] == 'created'


# 2. Тест: Перевірка оновлення статусу в БД
def test_repository_updates_status(dynamo_resource):
    repo = ShippingRepository()
    order_id = str(uuid.uuid4())
    shipping_id = repo.create_shipping("Ukr Poshta", ["p1"], order_id, "created", datetime.now())

    repo.update_shipping_status(shipping_id, "delivered")

    saved_shipping = repo.get_shipping(shipping_id)
    assert saved_shipping['shipping_status'] == "delivered"


# 3. Тест: Перевірка відправки повідомлення в SQS (Bottom-Up: Publisher)
def test_publisher_sends_message_to_sqs():
    publisher = ShippingPublisher()
    test_id = str(uuid.uuid4())

    msg_id = publisher.send_new_shipping(test_id)
    assert msg_id is not None

    # Read manually from SQS to verify
    sqs = boto3.client("sqs", endpoint_url=AWS_ENDPOINT_URL,
                       region_name=AWS_REGION,
                       aws_access_key_id="test",
                       aws_secret_access_key="test"
                       )
    queue_url = sqs.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)["Messages"]

    bodies = [m["Body"] for m in messages]
    assert test_id in bodies


# 4. Тест: Логіка валідації дати доставки (Top-Down: Service Logic)
def test_create_shipping_with_past_date_fails(real_shipping_service):
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(ValueError, match="must be greater than datetime now"):
        real_shipping_service.create_shipping("Meest Express", ["p1"], "ord1", past_date)


# 5. Тест: Логіка валідації типу доставки
def test_create_shipping_invalid_type_fails(real_shipping_service):
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(ValueError, match="Shipping type is not available"):
        real_shipping_service.create_shipping("InvalidType", ["p1"], "ord1", future_date)


# 6. Тест: Повний цикл - Створення та перевірка статусу (End-to-End flow)
def test_service_create_and_check_status(real_shipping_service):
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    s_id = real_shipping_service.create_shipping("Самовивіз", ["p1"], "ord1", future_date)

    # Одразу після створення статус має бути 'in progress' (бо сервіс робить update)
    status = real_shipping_service.check_status(s_id)
    assert status == ShippingService.SHIPPING_IN_PROGRESS


# 7. Тест: Обробка простроченої доставки (Process Shipping Batch)
def test_process_shipping_fails_if_expired(real_shipping_service):
    # 1. Створюємо доставку, яка "майже" прострочена
    # Хакаємо систему: створюємо через репозиторій напряму з минулою датою
    repo = ShippingRepository()
    s_id = repo.create_shipping("Nova Poshta", ["p1"], "ord_exp", "created",
                                datetime.now(timezone.utc) - timedelta(seconds=1))

    # 2. Викликаємо обробку конкретного ID
    real_shipping_service.process_shipping(s_id)

    # 3. Перевіряємо, що статус став FAILED
    status = real_shipping_service.check_status(s_id)
    assert status == ShippingService.SHIPPING_FAILED


# 8. Тест: Успішна обробка доставки
def test_process_shipping_completes_if_valid(real_shipping_service):
    # Створюємо валідну доставку
    repo = ShippingRepository()
    s_id = repo.create_shipping("Nova Poshta", ["p1"], "ord_ok", "created",
                                datetime.now(timezone.utc) + timedelta(days=1))

    # Обробляємо
    real_shipping_service.process_shipping(s_id)

    # Має бути COMPLETED
    status = real_shipping_service.check_status(s_id)
    assert status == ShippingService.SHIPPING_COMPLETED


# 9. Тест: Інтеграція Polling (отримання з черги і обробка)
def test_process_shipping_batch_integration(real_shipping_service):
    # Створюємо доставку через сервіс (вона потрапляє в чергу SQS)
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    s_id = real_shipping_service.create_shipping("Meest Express", ["p1"], "ord_batch", future_date)

    # Запускаємо обробку пакету (має вичитати з SQS і оновити статус)
    processed_results = real_shipping_service.process_shipping_batch()

    # Перевіряємо, чи є наш ID в результатах
    # process_shipping повертає метадані DynamoDB, перевіримо статус напряму
    status = real_shipping_service.check_status(s_id)
    assert status == ShippingService.SHIPPING_COMPLETED


# 10. Тест: Перевірка доступних типів доставки (Unit-like integration)
def test_list_available_shipping_types():
    types = ShippingService.list_available_shipping_type()
    assert "Нова Пошта" in types
    assert len(types) == 4