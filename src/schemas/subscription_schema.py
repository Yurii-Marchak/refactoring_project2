from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class AddSubscriptionRequest(BaseModel):
    """DTO for incoming request to add a new subscription."""
    user_id: UUID = Field(..., description="ID of the user adding the subscription")
    service_id: UUID = Field(..., description="ID of the selected service")
    tier_name: str = Field(..., min_length=1, description="Name of the selected tier (e.g., 'Premium')")

class SubscriptionResponse(BaseModel):
    """DTO for outgoing subscription data."""
    id: UUID
    user_id: UUID
    service_id: UUID
    tier_name: str
    start_date: datetime
    active: bool

    class Config:
        from_attributes = True  # Allows parsing directly from Domain Models (ORM mode)