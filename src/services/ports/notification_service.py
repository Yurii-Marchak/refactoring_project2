from abc import ABC, abstractmethod
from uuid import UUID

class INotificationService(ABC):
    """
    Outbound port for sending notifications to users.
    """
    @abstractmethod
    def send_notification(self, user_id: UUID, message: str) -> None:
        """Send a message to a specific user."""
        pass