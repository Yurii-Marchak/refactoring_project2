import pytest
from uuid import uuid4
from decimal import Decimal
from src.models.service import Service, SubscriptionTier, ServiceCategory
from src.storage.in_memory.service_repository import InMemoryServiceRepository

@pytest.fixture
def repo():
    return InMemoryServiceRepository()

def create_service(name: str, category: ServiceCategory) -> Service:
    tier = SubscriptionTier(name="Basic", price=Decimal("9.99"), features=["A"])
    return Service(name=name, category=category, tiers=[tier])

def test_save_and_get_all(repo):
    assert len(repo.get_all()) == 0
    
    svc1 = create_service("Net", ServiceCategory.STREAMING)
    svc2 = create_service("CloudX", ServiceCategory.CLOUD)
    
    repo.save(svc1)
    repo.save(svc2)
    
    all_svcs = repo.get_all()
    assert len(all_svcs) == 2
    names = {s.name for s in all_svcs}
    assert names == {"Net", "CloudX"}

def test_get_by_category(repo):
    repo.save(create_service("Stream1", ServiceCategory.STREAMING))
    repo.save(create_service("Stream2", ServiceCategory.STREAMING))
    repo.save(create_service("Game1", ServiceCategory.GAMING))
    
    streaming = repo.get_by_category(ServiceCategory.STREAMING)
    assert len(streaming) == 2
    for s in streaming:
        assert s.category == ServiceCategory.STREAMING
        
    gaming = repo.get_by_category("gaming") # testing string as well
    assert len(gaming) == 1
    
    education = repo.get_by_category(ServiceCategory.EDUCATION)
    assert len(education) == 0

def test_deep_copy_on_get_all(repo):
    svc = create_service("MutateMe", ServiceCategory.EDUCATION)
    repo.save(svc)
    
    fetched = repo.get_all()[0]
    fetched.tiers.append(SubscriptionTier(name="Pro", price=Decimal("19.99"), features=["B"]))
    
    second_fetch = repo.get_all()[0]
    assert len(second_fetch.tiers) == 1

def test_deep_copy_on_get_by_category(repo):
    svc = create_service("CopyCat", ServiceCategory.CLOUD)
    repo.save(svc)
    
    fetched = repo.get_by_category(ServiceCategory.CLOUD)[0]
    fetched.name = "Changed"
    
    second_fetch = repo.get_by_category(ServiceCategory.CLOUD)[0]
    assert second_fetch.name == "CopyCat"
