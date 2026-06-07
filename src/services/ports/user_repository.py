from abc import ABC, abstractmethod
from typing import Optional, Union
from uuid import UUID

from src.models.user import User

class IUserRepository(ABC):
    """
    Outbound port (interface) for User repository.
    Handles data persistence operations for User models.
    """

    @abstractmethod
    def get_by_id(self, user_id: Union[UUID, str]) -> Optional[User]:
        """Retrieve a user by their ID."""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Save a new user."""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user."""
        pass
