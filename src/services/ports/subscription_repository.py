from abc import ABC, abstractmethod
from typing import List, Union
from uuid import UUID

from src.models.subscription import UserSubscription

class ISubscriptionRepository(ABC):
    """
    Outbound port (interface) for UserSubscription repository.
    Handles data persistence operations for user subscriptions.
    """

    @abstractmethod
    def get_user_subscriptions(self, user_id: Union[UUID, str]) -> List[UserSubscription]:
        """Retrieve all subscriptions for a specific user."""
        pass

    @abstractmethod
    def add_subscription(self, subscription: UserSubscription) -> UserSubscription:
        """Add a new user subscription."""
        pass
    @abstractmethod
    def get_all(self) -> List[UserSubscription]:
        """Retrieve all subscriptions in the system."""
        pass
    