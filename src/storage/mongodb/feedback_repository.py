from pymongo.collection import Collection
from typing import List, Union
from uuid import UUID

from src.models.feedback import UsageFeedback
from src.services.ports.feedback_repository import IFeedbackRepository

class MongoFeedbackRepository(IFeedbackRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def save_feedback(self, feedback: UsageFeedback) -> UsageFeedback:
        doc = feedback.model_dump(mode='json')
        self.collection.insert_one(doc)
        return feedback

    def get_feedback_history(self, subscription_id: Union[UUID, str]) -> List[UsageFeedback]:
        cursor = self.collection.find({"user_subscription_id": str(subscription_id)})
        return [UsageFeedback(**doc) for doc in cursor]