from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

class RecommendationResponse(BaseModel):
    """DTO for outgoing optimization recommendation."""
    user_subscription_id: UUID
    service_name: str
    current_tier: str
    utility_score: float
    suggested_action: str
    estimated_monthly_savings: Decimal

    class Config:
        from_attributes = True