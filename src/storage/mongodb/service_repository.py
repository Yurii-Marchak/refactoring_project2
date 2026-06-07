from pymongo.collection import Collection
from typing import List

from src.models.service import Service
from src.services.ports.service_repository import IServiceRepository

class MongoServiceRepository(IServiceRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_all(self) -> List[Service]:
        cursor = self.collection.find()
        return [Service(**doc) for doc in cursor]

    def get_by_category(self, category: str) -> List[Service]:
        category_str = category.value if hasattr(category, 'value') else str(category)
        cursor = self.collection.find({"category": category_str})
        return [Service(**doc) for doc in cursor]
        
    def save(self, service: Service) -> Service:
        doc = service.model_dump(mode='json')
        self.collection.insert_one(doc)
        return service