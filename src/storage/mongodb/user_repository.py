from pymongo.collection import Collection
from typing import Optional, Union
from uuid import UUID

from src.models.user import User
from src.services.ports.user_repository import IUserRepository

class MongoUserRepository(IUserRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_by_id(self, user_id: Union[UUID, str]) -> Optional[User]:
        doc = self.collection.find_one({"id": str(user_id)})
        return User(**doc) if doc else None

    def save(self, user: User) -> User:
        doc = user.model_dump(mode='json')
        self.collection.insert_one(doc)
        return user

    def update(self, user: User) -> User:
        doc = user.model_dump(mode='json')
        res = self.collection.replace_one({"id": str(user.id)}, doc)
        if res.matched_count == 0:
            raise ValueError(f"User with id {user.id} not found.")
        return user