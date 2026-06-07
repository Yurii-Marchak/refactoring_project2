import pytest
from unittest.mock import Mock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from src.models.user import User
from src.models.service import Service, ServiceCategory, SubscriptionTier
from src.models.subscription import UserSubscription
from src.services.use_cases.optimization_strategies import StreamingOptimizationStrategy, GamingOptimizationStrategy
from src.services.use_cases.recommendation_use_case import GenerateRecommendationsUseCase
from src.services.use_cases.fuzzy_logic import FuzzyUtilityCalculator

@pytest.fixture
def base_service():
    return Service(
        id=uuid4(),
        name="TestFlix",
        category=ServiceCategory.STREAMING,
        tiers=[
            SubscriptionTier(name="Basic", price=Decimal("5.99")),
            SubscriptionTier(name="Premium", price=Decimal("15.99"))
        ]
    )

@pytest.fixture
def base_subscription(base_service):
    return UserSubscription(
        id=uuid4(),
        user_id=uuid4(),
        service_id=base_service.id,
        tier_name="Premium",
        start_date=datetime.now(),
        active=True
    )


def test_streaming_strategy_high_score(base_subscription, base_service):
    strategy = StreamingOptimizationStrategy()
    result = strategy.analyze(base_subscription, base_service, 85.0)
    assert result is None

def test_streaming_strategy_low_score_cancel(base_subscription, base_service):
    strategy = StreamingOptimizationStrategy()
    result = strategy.analyze(base_subscription, base_service, 20.0)
    assert result is not None
    assert "Відмовитися від підписки" in result.action
    assert result.savings == Decimal("15.99")

def test_streaming_strategy_medium_score_downgrade(base_subscription, base_service):
    strategy = StreamingOptimizationStrategy()
    result = strategy.analyze(base_subscription, base_service, 55.0)
    assert result is not None
    assert "Перейти на дешевший тариф 'Basic'" in result.action
    assert result.savings == Decimal("10.00")


def test_generate_recommendations_success(base_subscription, base_service):

    user_id = base_subscription.user_id
    mock_user = User(id=user_id, email="test@test.com")
    
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = mock_user
    
    mock_sub_repo = Mock()
    mock_sub_repo.get_user_subscriptions.return_value = [base_subscription]
    
    mock_service_repo = Mock()
    mock_service_repo.get_all.return_value = [base_service]
    
    mock_feedback_repo = Mock()

    
    mock_fuzzy = Mock(spec=FuzzyUtilityCalculator)
    mock_fuzzy.calculate_utility.return_value = 25.0

    use_case = GenerateRecommendationsUseCase(
        user_repo=mock_user_repo,
        subscription_repo=mock_sub_repo,
        service_repo=mock_service_repo,
        feedback_repo=mock_feedback_repo,
        fuzzy_calculator=mock_fuzzy
    )


    recommendations = use_case.execute(user_id)


    assert len(recommendations) == 1
    rec = recommendations[0]
    assert rec.service_name == "TestFlix"
    assert rec.current_tier == "Premium"
    assert rec.utility_score == 25.0
    assert "Відмовитися" in rec.suggested_action
    assert rec.estimated_monthly_savings == Decimal("15.99")

def test_generate_recommendations_user_not_found():
    mock_user_repo = Mock()
    mock_user_repo.get_by_id.return_value = None
    
    use_case = GenerateRecommendationsUseCase(mock_user_repo, Mock(), Mock(), Mock(), Mock())
    
    with pytest.raises(ValueError, match="not found"):
        use_case.execute(uuid4())