from abc import ABC, abstractmethod
from typing import List, Set
from uuid import UUID
from decimal import Decimal

from src.services.ports.notification_service import INotificationService
from src.services.ports.subscription_repository import ISubscriptionRepository

class IPriceChangeObserver(ABC):
    """Abstract Observer interface for price changes."""
    @abstractmethod
    def on_price_changed(self, service_id: UUID, tier_name: str, new_price: Decimal) -> None:
        pass

class PriceChangeSubject:
    """
    The Subject (Publisher) that maintains a list of observers 
    and notifies them of price changes.
    """
    def __init__(self):
        self._observers: List[IPriceChangeObserver] = []

    def attach(self, observer: IPriceChangeObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IPriceChangeObserver) -> None:
        self._observers.remove(observer)

    def change_price(self, service_id: UUID, tier_name: str, new_price: Decimal) -> None:
        """Simulates a price change and triggers notifications."""
        # Here would be the logic to update the Service model in the DB
        # ...
        # Notify all subscribers
        for observer in self._observers:
            observer.on_price_changed(service_id, tier_name, new_price)

class UserNotificationObserver(IPriceChangeObserver):
    """
    Concrete Observer that finds affected users and sends them notifications.
    """
    def __init__(self, subscription_repo: ISubscriptionRepository, notification_service: INotificationService):
        self.subscription_repo = subscription_repo
        self.notification_service = notification_service

    def on_price_changed(self, service_id: UUID, tier_name: str, new_price: Decimal) -> None:
        all_subs = self.subscription_repo.get_all()
        affected_users: Set[UUID] = set()

        for sub in all_subs:
            if sub.service_id == service_id and sub.tier_name == tier_name and sub.active:
                affected_users.add(sub.user_id)

        for user_id in affected_users:
            message = f"Увага! Вартість вашого тарифу '{tier_name}' змінилася. Нова ціна: {new_price}."
            self.notification_service.send_notification(user_id, message)