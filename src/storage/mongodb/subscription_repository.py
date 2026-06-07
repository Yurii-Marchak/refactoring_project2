from pymongo.collection import Collection
from typing import List, Union
from uuid import UUID

from src.models.subscription import UserSubscription
from src.services.ports.subscription_repository import ISubscriptionRepository

class MongoSubscriptionRepository(ISubscriptionRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_user_subscriptions(self, user_id: Union[UUID, str]) -> List[UserSubscription]:
        cursor = self.collection.find({"user_id": str(user_id)})
        return [UserSubscription(**doc) for doc in cursor]

    def add_subscription(self, subscription: UserSubscription) -> UserSubscription:
        doc = subscription.model_dump(mode='json')
        self.collection.insert_one(doc)
        return subscription
        
    def get_all(self) -> List[UserSubscription]:
        cursor = self.collection.find()
        return [UserSubscription(**doc) for doc in cursor]