import copy
from typing import Optional, Union, Dict
from uuid import UUID

from src.models.user import User
from src.services.ports.user_repository import IUserRepository

class InMemoryUserRepository(IUserRepository):
    """
    In-Memory implementation of IUserRepository.
    Uses a dictionary for O(1) storage and retrieval.
    Deep copies objects to avoid reference mutations.
    """
    
    def __init__(self):
        self._storage: Dict[str, User] = {}

    def get_by_id(self, user_id: Union[UUID, str]) -> Optional[User]:
        str_id = str(user_id)
        user = self._storage.get(str_id)
        return copy.deepcopy(user) if user else None

    def save(self, user: User) -> User:
        str_id = str(user.id)
        self._storage[str_id] = copy.deepcopy(user)
        return copy.deepcopy(self._storage[str_id])

    def update(self, user: User) -> User:
        str_id = str(user.id)
        if str_id not in self._storage:
            raise ValueError(f"User with id {str_id} not found.")
        self._storage[str_id] = copy.deepcopy(user)
        return copy.deepcopy(self._storage[str_id])
