from fastapi import APIRouter, Request, Depends, Form, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from uuid import UUID
from src.main import get_subscription_repository

# Імпортуємо наші Use Cases та провайдери залежностей з головного файлу
from src.main import (
    get_user_repository,
    get_service_repository,
    get_subscription_repository,
    get_recommendations_use_case
)

# Створюємо роутер (include_in_schema=False приховує його зі Swagger документації API)
router = APIRouter(prefix="/web", tags=["Web UI"], include_in_schema=False)
templates = Jinja2Templates(directory="src/templates")

def get_all_users_safe(user_repo):
    """Допоміжна функція для отримання всіх користувачів незалежно від типу бази даних."""
    if hasattr(user_repo, 'collection'):  # Якщо це MongoDB
        from src.models.user import User
        return [User(**doc) for doc in user_repo.collection.find()]
    else:  # Якщо це In-Memory
        return list(user_repo._storage.values())

@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    user_repo=Depends(get_user_repository),
    sub_repo=Depends(get_subscription_repository) # Додали репозиторій підписок
):
    """Головна сторінка (Дашборд)."""
    users_list = get_all_users_safe(user_repo)
    subs_count = 0
    
    # Якщо користувач авторизований, рахуємо його активні підписки
    if user_id:
        try:
            active_subs = [s for s in sub_repo.get_user_subscriptions(UUID(user_id)) if s.active]
            subs_count = len(active_subs)
        except ValueError:
            pass

    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request,
        "users_list": users_list,
        "current_user_id": user_id,
        "subs_count": subs_count
    })

@router.post("/set-user")
def set_user(user_id: str = Form(...)):
    """Ендпоінт для імітації авторизації (встановлює cookie та редиректить назад)."""
    response = RedirectResponse(url="/web/", status_code=303)
    response.set_cookie(key="user_id", value=user_id, httponly=True)
    return response

@router.get("/catalog", response_class=HTMLResponse)
def catalog(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    user_repo=Depends(get_user_repository),
    service_repo=Depends(get_service_repository)
):
    """Сторінка каталогу всіх доступних сервісів."""
    users_list = get_all_users_safe(user_repo)
    services = service_repo.get_all()
    return templates.TemplateResponse(request=request, name="catalog.html", context={
        "request": request,
        "users_list": users_list,
        "current_user_id": user_id,
        "services": services
    })

@router.get("/subscriptions", response_class=HTMLResponse)
def subscriptions(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    user_repo=Depends(get_user_repository),
    sub_repo=Depends(get_subscription_repository),
    service_repo=Depends(get_service_repository)
):
    """Сторінка активних підписок обраного користувача."""
    users_list = get_all_users_safe(user_repo)
    user_subs = []
    services_map = {}
    
    if user_id:
        try:
            user_subs = sub_repo.get_user_subscriptions(UUID(user_id))
            services_map = {str(s.id): s for s in service_repo.get_all()}
        except ValueError:
            pass

    return templates.TemplateResponse(request=request, name="subscriptions.html", context={
        "request": request,
        "users_list": users_list,
        "current_user_id": user_id,
        "subscriptions": user_subs,
        "services_map": services_map
    })

@router.get("/analytics", response_class=HTMLResponse)
def analytics(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    user_repo=Depends(get_user_repository),
    use_case=Depends(get_recommendations_use_case)
):
    """Головна сторінка аналітики та оптимізації."""
    users_list = get_all_users_safe(user_repo)
    recommendations = []
    
    if user_id:
        try:
            recommendations = use_case.execute(UUID(user_id))
        except ValueError:
            pass 

    return templates.TemplateResponse(request=request, name="analytics.html", context={
        "request": request,
        "users_list": users_list,
        "current_user_id": user_id,
        "recommendations": recommendations
    })