import pytest
from uuid import uuid4
from src.models.feedback import UsageFeedback
from src.services.use_cases.fuzzy_logic import FuzzyUtilityCalculator

@pytest.fixture
def calculator():
    return FuzzyUtilityCalculator()

def test_calculate_utility_empty_list(calculator):
    assert calculator.calculate_utility([]) == 0.0

def test_calculate_utility_max_values(calculator):
    # frequency=7 (norm=1.0), necessity=5 (norm=1.0) -> Score: 100.0
    fb = UsageFeedback(
        user_subscription_id=uuid4(),
        month_year="2026-01",
        frequency_1_to_7=7,
        necessity_1_to_5=5
    )
    assert calculator.calculate_utility([fb]) == 100.0

def test_calculate_utility_min_values(calculator):
    # frequency=1 (norm=0.0), necessity=1 (norm=0.0) -> Score: 0.0
    fb = UsageFeedback(
        user_subscription_id=uuid4(),
        month_year="2026-01",
        frequency_1_to_7=1,
        necessity_1_to_5=1
    )
    assert calculator.calculate_utility([fb]) == 0.0

def test_calculate_utility_average_multiple_feedbacks(calculator):
    # FB1: max values (100.0)
    fb1 = UsageFeedback(user_subscription_id=uuid4(), month_year="2026-01", frequency_1_to_7=7, necessity_1_to_5=5)
    # FB2: min values (0.0)
    fb2 = UsageFeedback(user_subscription_id=uuid4(), month_year="2026-02", frequency_1_to_7=1, necessity_1_to_5=1)
    
    # Expected average: 50.0
    assert calculator.calculate_utility([fb1, fb2]) == 50.0

def test_calculate_utility_mixed_weights(calculator):
    # frequency=4 (norm=3/6=0.5), necessity=3 (norm=2/4=0.5)
    # Score = (0.5 * 0.4 + 0.5 * 0.6) * 100 = 50.0
    fb = UsageFeedback(
        user_subscription_id=uuid4(),
        month_year="2026-01",
        frequency_1_to_7=4,
        necessity_1_to_5=3
    )
    assert calculator.calculate_utility([fb]) == 50.0