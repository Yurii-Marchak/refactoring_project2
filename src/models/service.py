from enum import Enum
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class ServiceCategory(str, Enum):
    """Enumeration of service categories."""
    STREAMING = "streaming"
    GAMING = "gaming"
    CLOUD = "cloud"
    EDUCATION = "education"

class SubscriptionTier(BaseModel):
    """
    Represents a specific tier of a subscription service (e.g., Basic, Premium).
    """
    name: str = Field(..., description="Name of the subscription tier")
    price: Decimal = Field(..., ge=0, description="Price of the tier, must not be negative")
    features: List[str] = Field(default_factory=list, description="List of features included in this tier")

class Service(BaseModel):
    """
    Represents a digital service offering subscriptions.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier of the service")
    name: str = Field(..., description="Name of the service")
    category: ServiceCategory = Field(..., description="Category of the service")
    tiers: List[SubscriptionTier] = Field(default_factory=list, description="List of available subscription tiers")
