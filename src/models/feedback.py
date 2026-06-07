from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class UsageFeedback(BaseModel):
    """
    Represents user feedback on their usage of a specific subscription.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the feedback")
    user_subscription_id: UUID = Field(..., description="Identifier of the associated user subscription")
    month_year: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Month and year of the feedback, format: YYYY-MM")
    frequency_1_to_7: int = Field(..., ge=1, le=7, description="Usage frequency rating from 1 to 7")
    necessity_1_to_5: int = Field(..., ge=1, le=5, description="Necessity rating from 1 to 5")
    specific_metric: Optional[Dict[str, Any]] = Field(default=None, description="Optional specific metrics for the category")
