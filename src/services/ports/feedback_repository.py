from abc import ABC, abstractmethod
from typing import List, Union
from uuid import UUID

from src.models.feedback import UsageFeedback

class IFeedbackRepository(ABC):
    """
    Outbound port (interface) for UsageFeedback repository.
    Handles data persistence operations for subscription usage feedback.
    """

    @abstractmethod
    def save_feedback(self, feedback: UsageFeedback) -> UsageFeedback:
        """Save a new usage feedback entry."""
        pass

    @abstractmethod
    def get_feedback_history(self, subscription_id: Union[UUID, str]) -> List[UsageFeedback]:
        """Retrieve feedback history for a specific user subscription."""
        pass
