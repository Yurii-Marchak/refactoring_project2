import copy
from typing import List, Union, Dict
from uuid import UUID

from src.models.subscription import UserSubscription
from src.services.ports.subscription_repository import ISubscriptionRepository

class InMemorySubscriptionRepository(ISubscriptionRepository):
    """
    In-Memory implementation of ISubscriptionRepository.
    Uses a dictionary for O(1) storage.
    Deep copies objects to avoid reference mutations.
    """

    def __init__(self):
        self._storage: Dict[str, UserSubscription] = {}

    def get_user_subscriptions(self, user_id: Union[UUID, str]) -> List[UserSubscription]:
        str_id = str(user_id)
        filtered = [
            sub for sub in self._storage.values()
            if str(sub.user_id) == str_id
        ]
        return [copy.deepcopy(sub) for sub in filtered]

    def add_subscription(self, subscription: UserSubscription) -> UserSubscription:
        str_id = str(subscription.id)
        self._storage[str_id] = copy.deepcopy(subscription)
        return copy.deepcopy(self._storage[str_id])

    def get_all(self) -> List[UserSubscription]:
        return [copy.deepcopy(sub) for sub in self._storage.values()]
