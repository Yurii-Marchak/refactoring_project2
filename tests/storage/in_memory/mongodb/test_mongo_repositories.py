import pytest
import mongomock
from uuid import uuid4
from datetime import datetime

from src.models.user import User
from src.models.service import Service, ServiceCategory, SubscriptionTier
from src.models.subscription import UserSubscription
from src.models.feedback import UsageFeedback

from src.storage.mongodb.user_repository import MongoUserRepository
from src.storage.mongodb.service_repository import MongoServiceRepository
from src.storage.mongodb.subscription_repository import MongoSubscriptionRepository
from src.storage.mongodb.feedback_repository import MongoFeedbackRepository

@pytest.fixture
def mongo_db():
    # Використовуємо mongomock замість реального сервера
    client = mongomock.MongoClient()
    return client.test_db

def test_mongo_user_repository(mongo_db):
    repo = MongoUserRepository(mongo_db.users)
    
    # Test Save
    user = User(id=uuid4(), email="mongo@test.com", preferences={})
    repo.save(user)
    
    # Test Get
    fetched = repo.get_by_id(user.id)
    assert fetched is not None
    assert fetched.email == "mongo@test.com"
    
    # Test Update
    user.email = "updated@test.com"
    repo.update(user)
    fetched_updated = repo.get_by_id(user.id)
    assert fetched_updated.email == "updated@test.com"

def test_mongo_service_repository(mongo_db):
    repo = MongoServiceRepository(mongo_db.services)
    
    service = Service(
        id=uuid4(), name="TestCloud", category=ServiceCategory.CLOUD, 
        tiers=[SubscriptionTier(name="Basic", price=9.99)]
    )
    repo.save(service)
    
    all_services = repo.get_all()
    assert len(all_services) == 1
    assert all_services[0].name == "TestCloud"
    
    cloud_services = repo.get_by_category(ServiceCategory.CLOUD)
    assert len(cloud_services) == 1
    
    gaming_services = repo.get_by_category(ServiceCategory.GAMING)
    assert len(gaming_services) == 0

def test_mongo_subscription_repository(mongo_db):
    repo = MongoSubscriptionRepository(mongo_db.subscriptions)
    user_id = uuid4()
    
    sub = UserSubscription(
        id=uuid4(), user_id=user_id, service_id=uuid4(),
        tier_name="Premium", start_date=datetime.now(), active=True
    )
    repo.add_subscription(sub)
    
    user_subs = repo.get_user_subscriptions(user_id)
    assert len(user_subs) == 1
    assert user_subs[0].tier_name == "Premium"

def test_mongo_feedback_repository(mongo_db):
    repo = MongoFeedbackRepository(mongo_db.feedbacks)
    sub_id = uuid4()
    
    fb = UsageFeedback(
        id=uuid4(), user_subscription_id=sub_id, month_year="2026-06",
        frequency_1_to_7=5, necessity_1_to_5=4
    )
    repo.save_feedback(fb)
    
    history = repo.get_feedback_history(sub_id)
    assert len(history) == 1
    assert history[0].month_year == "2026-06"