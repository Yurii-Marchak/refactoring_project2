import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError
from src.models.subscription import UserSubscription

def test_create_user_subscription_success():
    user_id = uuid4()
    service_id = uuid4()
    start_date = datetime(2026, 6, 1)
    
    subscription = UserSubscription(
        user_id=user_id,
        service_id=service_id,
        tier_name="Premium",
        start_date=start_date
    )
    
    assert subscription.user_id == user_id
    assert subscription.service_id == service_id
    assert subscription.tier_name == "Premium"
    assert subscription.start_date == start_date
    assert subscription.active is True

def test_create_user_subscription_inactive():
    user_id = uuid4()
    service_id = uuid4()
    start_date = datetime(2026, 6, 1)
    
    subscription = UserSubscription(
        user_id=user_id,
        service_id=service_id,
        tier_name="Basic",
        start_date=start_date,
        active=False
    )
    
    assert subscription.active is False

def test_create_user_subscription_missing_fields():
    with pytest.raises(ValidationError):
        UserSubscription(user_id=uuid4())
