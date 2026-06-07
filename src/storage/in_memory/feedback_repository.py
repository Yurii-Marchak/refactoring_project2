import copy
from typing import List, Union, Dict
from uuid import UUID

from src.models.feedback import UsageFeedback
from src.services.ports.feedback_repository import IFeedbackRepository

class InMemoryFeedbackRepository(IFeedbackRepository):
    """
    In-Memory implementation of IFeedbackRepository.
    Uses a dictionary for O(1) storage.
    Deep copies objects to avoid reference mutations.
    """

    def __init__(self):
        self._storage: Dict[str, UsageFeedback] = {}

    def save_feedback(self, feedback: UsageFeedback) -> UsageFeedback:
        str_id = str(feedback.id)
        self._storage[str_id] = copy.deepcopy(feedback)
        return copy.deepcopy(self._storage[str_id])

    def get_feedback_history(self, subscription_id: Union[UUID, str]) -> List[UsageFeedback]:
        str_sub_id = str(subscription_id)
        filtered = [
            fb for fb in self._storage.values()
            if str(fb.user_subscription_id) == str_sub_id
        ]
        return [copy.deepcopy(fb) for fb in filtered]
