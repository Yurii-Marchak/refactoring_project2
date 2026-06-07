import pytest
from datetime import datetime, timezone
from uuid import uuid4
from src.models.subscription import UserSubscription
from src.storage.in_memory.subscription_repository import InMemorySubscriptionRepository

@pytest.fixture
def repo():
    return InMemorySubscriptionRepository()

def create_sub(user_id) -> UserSubscription:
    return UserSubscription(
        user_id=user_id,
        service_id=uuid4(),
        tier_name="Premium",
        start_date=datetime.now(timezone.utc),
        active=True
    )

def test_add_and_get_user_subscriptions(repo):
    user_id_1 = uuid4()
    user_id_2 = uuid4()
    
    sub1 = create_sub(user_id_1)
    sub2 = create_sub(user_id_1)
    sub3 = create_sub(user_id_2)
    
    repo.add_subscription(sub1)
    repo.add_subscription(sub2)
    repo.add_subscription(sub3)
    
    user1_subs = repo.get_user_subscriptions(user_id_1)
    assert len(user1_subs) == 2
    
    user2_subs = repo.get_user_subscriptions(user_id_2)
    assert len(user2_subs) == 1
    assert user2_subs[0].id == sub3.id

def test_get_user_subscriptions_empty(repo):
    subs = repo.get_user_subscriptions(uuid4())
    assert len(subs) == 0

def test_deep_copy_on_add(repo):
    user_id = uuid4()
    sub = create_sub(user_id)
    repo.add_subscription(sub)
    
    sub.tier_name = "Basic"
    fetched = repo.get_user_subscriptions(user_id)[0]
    
    assert fetched.tier_name == "Premium"

def test_deep_copy_on_get(repo):
    user_id = uuid4()
    sub = create_sub(user_id)
    repo.add_subscription(sub)
    
    fetched = repo.get_user_subscriptions(user_id)[0]
    fetched.active = False
    
    second_fetch = repo.get_user_subscriptions(user_id)[0]
    assert second_fetch.active is True
