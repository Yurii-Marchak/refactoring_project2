import pytest
from fastapi.testclient import TestClient
from src.main import app, user_repo_instance

client = TestClient(app)

def test_set_user_cookie_redirects():

    user_id = list(user_repo_instance._storage.keys())[0]
    

    response = client.post(
        "/web/set-user", 
        data={"user_id": user_id}, 
        follow_redirects=False
    )
    
    assert response.status_code == 303
    assert response.headers["location"] == "/web/"
    

    assert "user_id" in response.cookies
    assert response.cookies["user_id"] == user_id

def test_web_routes_accessibility():


    routes = ["/web/", "/web/catalog", "/web/subscriptions", "/web/analytics"]
    
    for route in routes:
        response = client.get(route)

        assert response.status_code != 404