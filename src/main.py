from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from pymongo import MongoClient
from src.config import settings
from src.storage.mongodb.user_repository import MongoUserRepository
from src.storage.mongodb.service_repository import MongoServiceRepository
from src.storage.mongodb.subscription_repository import MongoSubscriptionRepository
from src.storage.mongodb.feedback_repository import MongoFeedbackRepository

from fastapi import FastAPI, Depends, HTTPException
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

# Domain Models
from src.models.user import User
from src.models.service import Service
from src.models.subscription import UserSubscription
from src.models.feedback import UsageFeedback

# Schemas (DTOs)
from src.schemas.subscription_schema import AddSubscriptionRequest, SubscriptionResponse
from src.schemas.recommendation_schema import RecommendationResponse

# Repositories (Ports & In-Memory Adapters)
from src.storage.in_memory.user_repository import InMemoryUserRepository
from src.storage.in_memory.service_repository import InMemoryServiceRepository
from src.storage.in_memory.subscription_repository import InMemorySubscriptionRepository
from src.storage.in_memory.feedback_repository import InMemoryFeedbackRepository

# Use Cases & Utilities
from src.services.use_cases.fuzzy_logic import FuzzyUtilityCalculator
from src.services.use_cases.recommendation_use_case import GenerateRecommendationsUseCase
from src.utils.data_factory import DataSeeder

app = FastAPI(
    title="SubOptima API", 
    description="Сервіс аналізу та оптимізації витрат на цифрові підписки", 
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Додаємо автоматичне створення папки
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- ВИБІР СЕРЕДОВИЩА ТА ІНІЦІАЛІЗАЦІЯ БД ---
if settings.STORAGE_TYPE == "mongodb":
    print("Starting in MONGODB mode...")
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    user_repo_instance = MongoUserRepository(db.users)
    service_repo_instance = MongoServiceRepository(db.services)
    subscription_repo_instance = MongoSubscriptionRepository(db.subscriptions)
    feedback_repo_instance = MongoFeedbackRepository(db.feedbacks)
    
    # Генеруємо початкові дані тільки якщо база порожня
    if db.services.count_documents({}) == 0:
        seeder = DataSeeder(user_repo_instance, service_repo_instance, subscription_repo_instance, feedback_repo_instance)
        seeder.seed_all()
else:
    print("Starting in IN-MEMORY mode...")
    user_repo_instance = InMemoryUserRepository()
    service_repo_instance = InMemoryServiceRepository()
    subscription_repo_instance = InMemorySubscriptionRepository()
    feedback_repo_instance = InMemoryFeedbackRepository()
    
    seeder = DataSeeder(user_repo_instance, service_repo_instance, subscription_repo_instance, feedback_repo_instance)
    seeder.seed_all()


# --- Dependency Providers ---
def get_user_repository():
    return user_repo_instance

def get_service_repository():
    return service_repo_instance

def get_subscription_repository():
    return subscription_repo_instance

def get_feedback_repository():
    return feedback_repo_instance

def get_fuzzy_calculator():
    return FuzzyUtilityCalculator()

def get_recommendations_use_case(
    u_repo=Depends(get_user_repository),
    sub_repo=Depends(get_subscription_repository),
    srv_repo=Depends(get_service_repository),
    fb_repo=Depends(get_feedback_repository),
    calc=Depends(get_fuzzy_calculator)
) -> GenerateRecommendationsUseCase:
    return GenerateRecommendationsUseCase(
        user_repo=u_repo,
        subscription_repo=sub_repo,
        service_repo=srv_repo,
        feedback_repo=fb_repo,
        fuzzy_calculator=calc
    )

# --- Ендпоінти (Endpoints) ---

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "SubOptima API is running"}

@app.get("/users", response_model=List[User], tags=["Users"])
def get_users(user_repo=Depends(get_user_repository)):
    """Отримати всіх зареєстрованих користувачів."""
    return list(user_repo._storage.values())

@app.post("/users", response_model=User, status_code=201, tags=["Users"])
def create_user(email: str, user_repo=Depends(get_user_repository)):
    """Створити нового користувача за email."""
    new_user = User(id=uuid4(), email=email, preferences={})
    return user_repo.save(new_user)

@app.get("/services", response_model=List[Service], tags=["Services"])
def get_services(service_repo=Depends(get_service_repository)):
    """Отримати повний каталог доступних цифрових сервісів та їхніх тарифів (16 сервісів)."""
    return service_repo.get_all()

@app.post("/subscriptions", response_model=SubscriptionResponse, status_code=201, tags=["Subscriptions"])
def add_subscription(request: AddSubscriptionRequest, sub_repo=Depends(get_subscription_repository), srv_repo=Depends(get_service_repository)):
    """Додати нову підписку для користувача на основі обраного сервісу та тарифу."""
    # Перевіряємо, чи існує такий сервіс в базі
    all_services = {str(s.id): s for s in srv_repo.get_all()}
    service = all_services.get(str(request.service_id))
    if not service:
        raise HTTPException(status_code=404, detail="Обраний цифровий сервіс не знайдено.")

    # Перевіряємо, чи існує такий тариф у сервісі
    tier_exists = any(t.name.lower() == request.tier_name.lower() for t in service.tiers)
    if not tier_exists:
        raise HTTPException(status_code=400, detail=f"Тариф '{request.tier_name}' відсутній для сервісу {service.name}.")

    new_sub = UserSubscription(
        id=uuid4(),
        user_id=request.user_id,
        service_id=request.service_id,
        tier_name=request.tier_name,
        start_date=datetime.now(),
        active=True
    )
    return sub_repo.add_subscription(new_sub)

@app.post("/feedback", status_code=201, tags=["Feedback"])
def submit_feedback(feedback: UsageFeedback, feedback_repo=Depends(get_feedback_repository)):
    """Зберегти щомісячний фідбек користувача про інтенсивність використання підписки."""
    return feedback_repo.save_feedback(feedback)

@app.get("/recommendations/{user_id}", response_model=List[RecommendationResponse], tags=["Optimization"])
def get_recommendations(user_id: UUID, use_case=Depends(get_recommendations_use_case)):
    """
    Головний ендпоінт аналітики: обчислює Індекс Корисності за допомогою нечіткої логіки
    та повертає індивідуальні рекомендації щодо оптимізації витрат.
    """
    try:
        return use_case.execute(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
from src.routers.web import router as web_router
app.include_router(web_router)