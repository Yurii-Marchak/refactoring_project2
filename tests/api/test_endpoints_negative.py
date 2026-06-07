import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.main import app, service_repo_instance

client = TestClient(app)


def test_post_subscription_service_not_found():
    """Перевірка помилки 404, якщо вказано неіснуючий сервіс."""
    payload = {
        "user_id": str(uuid4()), 
        "service_id": str(uuid4()),
        "tier_name": "Basic"
    }
    response = client.post("/subscriptions", json=payload)
    assert response.status_code == 404
    assert "не знайдено" in response.json()["detail"].lower()

def test_post_subscription_tier_not_found():
    """Перевірка помилки 400, якщо обрано неіснуючий тариф для реального сервісу."""

    service = list(service_repo_instance._storage.values())[0]
    payload = {
        "user_id": str(uuid4()), 
        "service_id": str(service.id), 
        "tier_name": "SuperMegaPremium"
    }
    response = client.post("/subscriptions", json=payload)
    assert response.status_code == 400
    assert "відсутній" in response.json()["detail"].lower()

def test_post_subscription_empty_tier_name():
    """Перевірка помилки 422 від Pydantic (min_length=1) при порожньому тарифі."""
    payload = {"user_id": str(uuid4()), "service_id": str(uuid4()), "tier_name": ""}
    response = client.post("/subscriptions", json=payload)
    assert response.status_code == 422

def test_post_subscription_invalid_uuid_format():
    """Перевірка помилки 422, якщо ID передано не у форматі UUID."""
    payload = {"user_id": "not-a-uuid", "service_id": str(uuid4()), "tier_name": "Basic"}
    response = client.post("/subscriptions", json=payload)
    assert response.status_code == 422


def test_post_feedback_invalid_frequency():
    """Перевірка помилки 422, якщо частота використання виходить за межі 1-7."""
    payload = {
        "user_subscription_id": str(uuid4()), 
        "month_year": "2026-05", 
        "frequency_1_to_7": 8, 
        "necessity_1_to_5": 3
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 422

def test_post_feedback_invalid_necessity():
    """Перевірка помилки 422, якщо необхідність виходить за межі 1-5."""
    payload = {
        "user_subscription_id": str(uuid4()), 
        "month_year": "2026-05", 
        "frequency_1_to_7": 5, 
        "necessity_1_to_5": 6
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 422

def test_post_feedback_invalid_date_format():
    """Перевірка помилки 422 для неправильного формату дати (не YYYY-MM)."""
    payload = {
        "user_subscription_id": str(uuid4()), 
        "month_year": "2026/05", 
        "frequency_1_to_7": 5, 
        "necessity_1_to_5": 3
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 422


def test_get_recommendations_user_not_found():
    """Перевірка помилки 404, якщо користувача для аналітики не існує."""
    response = client.get(f"/recommendations/{uuid4()}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_recommendations_invalid_uuid():
    """Перевірка помилки 422, якщо замість UUID передано звичайний рядок."""
    response = client.get("/recommendations/invalid-id")
    assert response.status_code == 422

def test_create_user_missing_email():
    """Перевірка помилки 422 при спробі створити користувача без обов'язкового email."""
    response = client.post("/users") # Query-параметр email відсутній
    assert response.status_code == 422


def test_web_catalog_no_cookie_status_and_warning():
    """Перевірка: сторінка Каталогу віддає 200, але показує попередження, якщо немає кукі."""
    response = client.get("/web/catalog")
    assert response.status_code == 200
    assert "Оберіть користувача у меню вище" in response.text

def test_web_catalog_no_cookie_button_disabled():
    """Перевірка: кнопка 'Підписатися' заблокована (disabled), якщо немає кукі."""
    response = client.get("/web/catalog")
    assert response.status_code == 200

    assert "disabled" in response.text

def test_web_subscriptions_no_cookie():
    """Перевірка: сторінка Підписок віддає 200 та показує попередження-заглушку."""
    response = client.get("/web/subscriptions")
    assert response.status_code == 200
    assert "Будь ласка, оберіть користувача для перегляду підписок" in response.text

def test_web_analytics_no_cookie():
    """Перевірка: сторінка Аналітики віддає 200 та просить обрати користувача."""
    response = client.get("/web/analytics")
    assert response.status_code == 200
    assert "Оберіть користувача для генерації індивідуального звіту" in response.text

def test_web_dashboard_no_cookie():
    """Перевірка: Головна сторінка віддає 200 та показує попередження про авторизацію."""
    response = client.get("/web/")
    assert response.status_code == 200
    assert "Авторизація не виконана" in response.text

def test_web_set_user_missing_form_data():
    """Перевірка помилки 422, якщо форма /set-user відправлена порожньою."""
    response = client.post("/web/set-user", data={})
    assert response.status_code == 422