import pytest
from fastapi.testclient import TestClient
from uuid import uuid4, UUID
from src.main import app, user_repo_instance, service_repo_instance

client = TestClient(app)

def test_get_users_returns_seeded_users():
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Перевіряємо, що 3 користувачі успішно згенеровані Seeder-ом
    assert "@example.com" in data[0]["email"]

def test_create_user_success():
    email = "new_student@university.edu"
    response = client.post(f"/users?email={email}")
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert "id" in data

def test_get_services_returns_all_16_items():
    response = client.get("/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 16  # Сувора вимога ТЗ: 16 базових сервісів у каталозі

def test_add_subscription_success():
    # Отримуємо існуючого користувача та сервіс із бази даних
    user_id = list(user_repo_instance._storage.keys())[0]
    service = list(service_repo_instance._storage.values())[0]  # Наприклад, Netflix
    tier_name = service.tiers[0].name  # Basic

    payload = {
        "user_id": user_id,
        "service_id": str(service.id),
        "tier_name": tier_name
    }
    response = client.post("/subscriptions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["tier_name"] == tier_name
    assert data["active"] is True

def test_add_subscription_service_not_found():
    user_id = list(user_repo_instance._storage.keys())[0]
    payload = {
        "user_id": user_id,
        "service_id": str(uuid4()),  # Неіснуючий ID
        "tier_name": "Premium"
    }
    response = client.post("/subscriptions", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() or "не знайдено" in response.json()["detail"].lower()

def test_get_recommendations_for_active_geek():
    # Перший користувач - активний гік (high usage, не повинно бути пропозицій скасування)
    user_id = list(user_repo_instance._storage.keys())[0]
    response = client.get(f"/recommendations/{user_id}")
    assert response.status_code == 200
    # Активному користувачу сервіси потрібні, рекомендацій щодо економії може не бути або вони мінімальні
    assert isinstance(response.json(), list)

def test_get_recommendations_for_forgetful_payer():
    # Другий користувач платить, але не користується (low usage, очікуємо рекомендацію "Відмовитися")
    user_id = list(user_repo_instance._storage.keys())[1]
    response = client.get(f"/recommendations/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "відмовитися" in data[0]["suggested_action"].lower()

def test_get_recommendations_user_not_found():
    response = client.get(f"/recommendations/{uuid4()}")
    assert response.status_code == 404