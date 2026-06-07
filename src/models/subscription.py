from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class UserSubscription(BaseModel):
    """
    Represents a user's active or inactive subscription to a service tier.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier of the user subscription")
    user_id: UUID = Field(..., description="Identifier of the user who owns the subscription")
    service_id: UUID = Field(..., description="Identifier of the subscribed service")
    tier_name: str = Field(..., description="Name of the subscribed tier")
    start_date: datetime = Field(..., description="Date and time when the subscription started")
    active: bool = Field(default=True, description="Indicates if the subscription is currently active")
