import pytest
from uuid import uuid4
from decimal import Decimal
from pydantic import ValidationError

from src.models.user import User
from src.models.service import Service, ServiceCategory, SubscriptionTier
from src.models.feedback import UsageFeedback


def test_create_user_success():
    user_id = uuid4()
    user = User(id=user_id, email="test@suboptima.com", preferences={"theme": "dark"})
    
    assert user.id == user_id
    assert user.email == "test@suboptima.com"
    assert user.preferences["theme"] == "dark"

def test_create_service_success():
    tier1 = SubscriptionTier(name="Basic", price=Decimal("5.99"))
    tier2 = SubscriptionTier(name="Premium", price=Decimal("15.99"))
    
    service = Service(
        id=uuid4(),
        name="TestFlix",
        category=ServiceCategory.STREAMING,
        tiers=[tier1, tier2]
    )
    
    assert service.name == "TestFlix"
    assert service.category == ServiceCategory.STREAMING
    assert len(service.tiers) == 2
    assert service.tiers[1].price == Decimal("15.99")

def test_create_usage_feedback_success():
    sub_id = uuid4()
    feedback = UsageFeedback(
        user_subscription_id=sub_id,
        month_year="2026-05",
        frequency_1_to_7=5,
        necessity_1_to_5=4
    )
    
    assert feedback.user_subscription_id == sub_id
    assert feedback.month_year == "2026-05"
    assert feedback.frequency_1_to_7 == 5
    assert feedback.necessity_1_to_5 == 4


def test_subscription_tier_negative_price():
    """Перевірка, що не можна створити тариф із від'ємною ціною (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        SubscriptionTier(name="Basic", price=Decimal("-5.00"))
    
    assert "Input should be greater than or equal to 0" in str(exc_info.value)

@pytest.mark.parametrize("invalid_freq", [0, 8, -1, 100])
def test_usage_feedback_frequency_out_of_bounds(invalid_freq):
    """Перевірка обмежень для частоти використання (має бути від 1 до 7)."""
    with pytest.raises(ValidationError) as exc_info:
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year="2026-05",
            frequency_1_to_7=invalid_freq,
            necessity_1_to_5=3
        )
    assert "Input should be" in str(exc_info.value)

@pytest.mark.parametrize("invalid_nec", [0, 6, -5, 10])
def test_usage_feedback_necessity_out_of_bounds(invalid_nec):
    """Перевірка обмежень для необхідності (має бути від 1 до 5)."""
    with pytest.raises(ValidationError):
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year="2026-05",
            frequency_1_to_7=4,
            necessity_1_to_5=invalid_nec
        )

@pytest.mark.parametrize("invalid_date", [
    "2026/05",
    "05-2026",
    "2026-5",
    "26-05",
    "text",
])
def test_usage_feedback_invalid_month_year(invalid_date):
    """Перевірка регулярного виразу для формату YYYY-MM."""
    with pytest.raises(ValidationError) as exc_info:
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year=invalid_date,
            frequency_1_to_7=4,
            necessity_1_to_5=3
        )
    assert "String should match pattern" in str(exc_info.value)