import pytest
from uuid import uuid4
from pydantic import ValidationError
from src.models.feedback import UsageFeedback

def test_create_usage_feedback_success():
    sub_id = uuid4()
    feedback = UsageFeedback(
        user_subscription_id=sub_id,
        month_year="2026-06",
        frequency_1_to_7=5,
        necessity_1_to_5=4,
        specific_metric={"hours_watched": 45}
    )
    
    assert feedback.user_subscription_id == sub_id
    assert feedback.month_year == "2026-06"
    assert feedback.frequency_1_to_7 == 5
    assert feedback.necessity_1_to_5 == 4
    assert feedback.specific_metric == {"hours_watched": 45}

def test_usage_feedback_invalid_month_year():
    with pytest.raises(ValidationError):
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year="06-2026", # Invalid format
            frequency_1_to_7=5,
            necessity_1_to_5=4
        )

def test_usage_feedback_invalid_frequency():
    with pytest.raises(ValidationError):
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year="2026-06",
            frequency_1_to_7=8, # Out of bounds
            necessity_1_to_5=4
        )
        
    with pytest.raises(ValidationError):
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year="2026-06",
            frequency_1_to_7=0, # Out of bounds
            necessity_1_to_5=4
        )

def test_usage_feedback_invalid_necessity():
    with pytest.raises(ValidationError):
        UsageFeedback(
            user_subscription_id=uuid4(),
            month_year="2026-06",
            frequency_1_to_7=5,
            necessity_1_to_5=6 # Out of bounds
        )
