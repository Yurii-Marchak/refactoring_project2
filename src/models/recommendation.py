from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

class Recommendation(BaseModel):
    """
    Represents a specific optimization recommendation for a user's subscription.
    """
    user_subscription_id: UUID = Field(..., description="The ID of the analyzed subscription")
    service_name: str = Field(..., description="Name of the service (e.g., Netflix)")
    current_tier: str = Field(..., description="Current subscription tier")
    utility_score: float = Field(..., description="Calculated fuzzy logic score (0.0 - 100.0)")
    suggested_action: str = Field(..., description="Text description of the recommended action")
    estimated_monthly_savings: Decimal = Field(..., ge=0, description="How much money will be saved per month")