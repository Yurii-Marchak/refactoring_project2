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

# ==========================================
# РОЗШИРЕНІ ТЕСТИ: Нечітка логіка
# ==========================================

def test_utility_mixed_max_and_min(calculator):
    """Один відгук з максимальними балами (100.0), інший — з мінімальними (0.0)."""
    fb_max = create_feedback(7, 5)
    fb_min = create_feedback(1, 1)
    
    score = calculator.calculate_utility([fb_max, fb_min])
    assert score == 50.0  # Середнє має бути рівно 50

def test_utility_gradual_decrease_12_months(calculator):
    """Список з 12 відгуків, де оцінки поступово падають від максимуму до мінімуму."""
    feedbacks = []
    # Згенеруємо 12 відгуків, де показники поступово зменшуються
    for i in range(12):
        freq = max(1, 7 - (i // 2))  # 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2
        nec = max(1, 5 - (i // 3))   # 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2
        feedbacks.append(create_feedback(freq, nec))
        
    score = calculator.calculate_utility(feedbacks)
    # Оскільки бали падають, загальний Utility Score має бути десь посередині, але точно > 0 і < 100
    assert 40.0 < score < 70.0

def test_utility_rounding_exactness(calculator):
    """Перевірка округлення результату до рівно 2 знаків після коми."""
    # freq=2 (norm=1/6), nec=2 (norm=1/4). 
    # Score = ((1/6)*0.4 + (1/4)*0.6) * 100 = 21.666666...
    # Очікуємо точне математичне округлення до 21.67
    fb = create_feedback(2, 2)
    score = calculator.calculate_utility([fb])
    
    assert score == 21.67
    assert len(str(score).split('.')[1]) <= 2  # Перевіряємо формат дробової частини

def test_utility_high_frequency_low_necessity(calculator):
    """Висока частота, але нульова необхідність (перевірка ваги 40%)."""
    # freq=7 (norm=1.0), nec=1 (norm=0.0). Вага частоти = 0.4
    fb = create_feedback(7, 1)
    assert calculator.calculate_utility([fb]) == 40.0

def test_utility_low_frequency_high_necessity(calculator):
    """Низька частота, але максимальна необхідність (перевірка ваги 60%)."""
    # freq=1 (norm=0.0), nec=5 (norm=1.0). Вага необхідності = 0.6
    fb = create_feedback(1, 5)
    assert calculator.calculate_utility([fb]) == 60.0

def test_utility_median_values(calculator):
    """Абсолютно середні значення обох показників."""
    # freq=4 (norm=0.5), nec=3 (norm=0.5)
    fb = create_feedback(4, 3)
    assert calculator.calculate_utility([fb]) == 50.0

def test_utility_just_above_minimum(calculator):
    """Мінімальний крок вище абсолютного нуля."""
    # freq=2 (norm=1/6), nec=1 (norm=0)
    # (1/6 * 0.4) * 100 = 6.666... -> 6.67
    fb = create_feedback(2, 1)
    assert calculator.calculate_utility([fb]) == 6.67

def test_utility_just_below_maximum(calculator):
    """Мінімальний крок нижче абсолютного максимуму."""
    # freq=7 (norm=1.0), nec=4 (norm=0.75)
    # (1.0 * 0.4 + 0.75 * 0.6) * 100 = (0.4 + 0.45) * 100 = 85.0
    fb = create_feedback(7, 4)
    assert calculator.calculate_utility([fb]) == 85.0

def test_utility_massive_data_load(calculator):
    """Стрес-тест: 1000 відгуків з однаковими значеннями для перевірки стабільності циклу."""
    feedbacks = [create_feedback(4, 3) for _ in range(1000)]
    # Середнє значення 1000 однакових відгуків має залишитися 50.0
    assert calculator.calculate_utility(feedbacks) == 50.0

def test_utility_empty_list_returns_zero(calculator):
    """Граничний випадок: порожній список відгуків."""
    assert calculator.calculate_utility([]) == 0.0

def test_utility_identical_scores_averaging(calculator):
    """Масив із різних відгуків, що дають однаковий кінцевий бал."""
    # fb1: freq=7 (norm=1.0), nec=1 (norm=0.0) -> Score 40.0
    # fb2: freq=1 (norm=0.0), nec=5 (norm=1.0) -> Score 60.0
    # Average = 50.0
    fb1 = create_feedback(7, 1)
    fb2 = create_feedback(1, 5)
    
    assert calculator.calculate_utility([fb1, fb2]) == 50.0