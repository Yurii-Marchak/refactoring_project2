import pytest
from fastapi.testclient import TestClient
from src.main import app, user_repo_instance

client = TestClient(app)

def test_set_user_cookie_redirects():
    # Отримуємо реальний ID одного зі згенерованих користувачів
    user_id = list(user_repo_instance._storage.keys())[0]
    
    # Робимо POST запит з формою (application/x-www-form-urlencoded)
    response = client.post(
        "/web/set-user", 
        data={"user_id": user_id}, 
        follow_redirects=False # Не йдемо за редиректом, перевіряємо сам факт 303
    )
    
    assert response.status_code == 303
    assert response.headers["location"] == "/web/"
    
    # Перевіряємо, що Cookie успішно встановлено
    assert "user_id" in response.cookies
    assert response.cookies["user_id"] == user_id

def test_web_routes_accessibility():
    # Оскільки шаблонів ще немає, ми очікуємо 500 (TemplateNotFound),
    # але важливо перевірити, що маршрути зареєстровані і не повертають 404
    routes = ["/web/", "/web/catalog", "/web/subscriptions", "/web/analytics"]
    
    for route in routes:
        response = client.get(route)
        # 404 означало б, що роутер не підключився до main.py
        assert response.status_code != 404