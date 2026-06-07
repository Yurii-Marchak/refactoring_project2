from fastapi.testclient import TestClient
from src.main import (
    app, 
    get_recommendations_use_case,
    get_user_repository,
    get_subscription_repository,
    get_service_repository,
    get_feedback_repository,
    get_fuzzy_calculator
)

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "SubOptima API is running"}

def test_dependency_injection_resolution():
    """Перевіряє, що DI-контейнер правильно збирає Use Case із In-Memory сховищами"""
    u_repo = get_user_repository()
    sub_repo = get_subscription_repository()
    srv_repo = get_service_repository()
    fb_repo = get_feedback_repository()
    calc = get_fuzzy_calculator()
    
    use_case = get_recommendations_use_case(
        u_repo=u_repo,
        sub_repo=sub_repo,
        srv_repo=srv_repo,
        fb_repo=fb_repo,
        calc=calc
    )
    

    assert use_case.user_repo is u_repo
    assert use_case.service_repo is srv_repo
    assert use_case.fuzzy_calculator is calc