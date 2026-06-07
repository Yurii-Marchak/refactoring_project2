from fastapi import FastAPI, Depends

# Repositories
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

# --- Глобальні екземпляри (Singletons) для In-Memory БД ---
user_repo_instance = InMemoryUserRepository()
service_repo_instance = InMemoryServiceRepository()
subscription_repo_instance = InMemorySubscriptionRepository()
feedback_repo_instance = InMemoryFeedbackRepository()

# Наповнення бази початковими тестовими даними при старті
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

# Головний DI-провайдер для оркестратора
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

# Базовий ендпоінт для перевірки працездатності
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "SubOptima API is running"}