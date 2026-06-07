from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Dict, Any

class User(BaseModel):
    """
    Represents a user in the SubOptima system.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier of the user")
    email: str = Field(..., description="Email address of the user")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User specific preferences")
