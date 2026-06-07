import pytest
from uuid import uuid4

from src.models.feedback import UsageFeedback
from src.services.use_cases.fuzzy_logic import FuzzyUtilityCalculator

@pytest.fixture
def calculator():
    return FuzzyUtilityCalculator()

def create_feedback(freq: int, nec: int, month="2026-01") -> UsageFeedback:
    """Допоміжна функція для швидкої генерації відгуків у тестах."""
    return UsageFeedback(
        user_subscription_id=uuid4(),
        month_year=month,
        frequency_1_to_7=freq,
        necessity_1_to_5=nec
    )


def test_utility_mixed_max_and_min(calculator):
    """Один відгук з максимальними балами (100.0), інший — з мінімальними (0.0)."""
    fb_max = create_feedback(7, 5)
    fb_min = create_feedback(1, 1)
    
    score = calculator.calculate_utility([fb_max, fb_min])
    assert score == 50.0  # Середнє має бути рівно 50

def test_utility_gradual_decrease_12_months(calculator):
    """Список з 12 відгуків, де оцінки поступово падають від максимуму до мінімуму."""
    feedbacks = []

    for i in range(12):
        freq = max(1, 7 - (i // 2))
        nec = max(1, 5 - (i // 3))
        feedbacks.append(create_feedback(freq, nec))
        
    score = calculator.calculate_utility(feedbacks)

    assert 40.0 < score < 70.0

def test_utility_rounding_exactness(calculator):
    """Перевірка округлення результату до рівно 2 знаків після коми."""

    fb = create_feedback(2, 2)
    score = calculator.calculate_utility([fb])
    
    assert score == 21.67
    assert len(str(score).split('.')[1]) <= 2

def test_utility_high_frequency_low_necessity(calculator):
    """Висока частота, але нульова необхідність (перевірка ваги 40%)."""

    fb = create_feedback(7, 1)
    assert calculator.calculate_utility([fb]) == 40.0

def test_utility_low_frequency_high_necessity(calculator):
    """Низька частота, але максимальна необхідність (перевірка ваги 60%)."""

    fb = create_feedback(1, 5)
    assert calculator.calculate_utility([fb]) == 60.0

def test_utility_median_values(calculator):
    """Абсолютно середні значення обох показників."""

    fb = create_feedback(4, 3)
    assert calculator.calculate_utility([fb]) == 50.0

def test_utility_just_above_minimum(calculator):
    """Мінімальний крок вище абсолютного нуля."""

    fb = create_feedback(2, 1)
    assert calculator.calculate_utility([fb]) == 6.67

def test_utility_just_below_maximum(calculator):
    """Мінімальний крок нижче абсолютного максимуму."""

    fb = create_feedback(7, 4)
    assert calculator.calculate_utility([fb]) == 85.0

def test_utility_massive_data_load(calculator):
    """Стрес-тест: 1000 відгуків з однаковими значеннями для перевірки стабільності циклу."""
    feedbacks = [create_feedback(4, 3) for _ in range(1000)]

    assert calculator.calculate_utility(feedbacks) == 50.0

def test_utility_empty_list_returns_zero(calculator):
    """Граничний випадок: порожній список відгуків."""
    assert calculator.calculate_utility([]) == 0.0

def test_utility_identical_scores_averaging(calculator):
    """Масив із різних відгуків, що дають однаковий кінцевий бал."""

    fb1 = create_feedback(7, 1)
    fb2 = create_feedback(1, 5)
    
    assert calculator.calculate_utility([fb1, fb2]) == 50.0