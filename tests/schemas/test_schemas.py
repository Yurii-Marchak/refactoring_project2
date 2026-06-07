import pytest
from uuid import uuid4
from decimal import Decimal
from pydantic import ValidationError

from src.schemas.subscription_schema import AddSubscriptionRequest
from src.schemas.recommendation_schema import RecommendationResponse
from src.models.recommendation import Recommendation

def test_add_subscription_request_valid():
    req = AddSubscriptionRequest(
        user_id=uuid4(), 
        service_id=uuid4(), 
        tier_name="Premium"
    )
    assert req.tier_name == "Premium"

def test_add_subscription_request_invalid_empty_tier():
    with pytest.raises(ValidationError):
        # tier_name cannot be empty due to min_length=1
        AddSubscriptionRequest(
            user_id=uuid4(), 
            service_id=uuid4(), 
            tier_name=""
        )

def test_recommendation_response_from_domain_model():
    # Verify that the DTO properly parses data from the Domain Model (ORM mode)
    domain_model = Recommendation(
        user_subscription_id=uuid4(),
        service_name="Netflix",
        current_tier="Standard",
        utility_score=35.5,
        suggested_action="Cancel",
        estimated_monthly_savings=Decimal("10.99")
    )
    
    dto = RecommendationResponse.model_validate(domain_model)
    assert dto.service_name == "Netflix"
    assert dto.estimated_monthly_savings == Decimal("10.99")