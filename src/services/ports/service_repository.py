from abc import ABC, abstractmethod
from typing import List

from src.models.service import Service

class IServiceRepository(ABC):
    """
    Outbound port (interface) for Service repository.
    Handles data persistence operations for Service models.
    """

    @abstractmethod
    def get_all(self) -> List[Service]:
        """Retrieve all available services."""
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Service]:
        """Retrieve services filtered by their category."""
        pass
