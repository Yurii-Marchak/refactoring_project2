import pytest
from decimal import Decimal
from pydantic import ValidationError
from src.models.service import Service, SubscriptionTier, ServiceCategory

def test_create_subscription_tier_success():
    tier = SubscriptionTier(name="Premium", price=Decimal("15.99"), features=["4K", "No Ads"])
    assert tier.name == "Premium"
    assert tier.price == Decimal("15.99")
    assert tier.features == ["4K", "No Ads"]

def test_create_subscription_tier_negative_price():
    with pytest.raises(ValidationError):
        SubscriptionTier(name="Premium", price=Decimal("-5.00"))

def test_create_service_success():
    tier = SubscriptionTier(name="Basic", price=Decimal("5.00"))
    service = Service(name="Netflix", category=ServiceCategory.STREAMING, tiers=[tier])
    assert service.name == "Netflix"
    assert service.category == ServiceCategory.STREAMING
    assert len(service.tiers) == 1
    assert service.tiers[0].name == "Basic"

def test_create_service_invalid_category():
    with pytest.raises(ValidationError):
        Service(name="Netflix", category="invalid_category")
