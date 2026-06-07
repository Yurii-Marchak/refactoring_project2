import copy
from typing import List, Dict

from src.models.service import Service
from src.services.ports.service_repository import IServiceRepository

class InMemoryServiceRepository(IServiceRepository):
    """
    In-Memory implementation of IServiceRepository.
    Uses a dictionary for O(1) storage.
    Deep copies objects to avoid reference mutations.
    """
    
    def __init__(self):
        self._storage: Dict[str, Service] = {}

    def get_all(self) -> List[Service]:
        return [copy.deepcopy(service) for service in self._storage.values()]

    def get_by_category(self, category: str) -> List[Service]:
        category_str = category.value if hasattr(category, 'value') else str(category)
        
        filtered_services = [
            service for service in self._storage.values() 
            if (service.category.value if hasattr(service.category, 'value') else str(service.category)) == category_str
        ]
        return [copy.deepcopy(service) for service in filtered_services]
    
    def save(self, service: Service) -> Service:
        """
        Utility method to populate the in-memory repository.
        (Not strictly required by IServiceRepository, but needed for testing/mocking).
        """
        str_id = str(service.id)
        self._storage[str_id] = copy.deepcopy(service)
        return copy.deepcopy(self._storage[str_id])
