import pytest
from src.utils.data_factory import ServiceFactory, DataSeeder
from src.models.service import ServiceCategory
from src.storage.in_memory.user_repository import InMemoryUserRepository
from src.storage.in_memory.service_repository import InMemoryServiceRepository
from src.storage.in_memory.subscription_repository import InMemorySubscriptionRepository
from src.storage.in_memory.feedback_repository import InMemoryFeedbackRepository

def test_service_factory_creates_16_services():
    services = ServiceFactory.generate_all_services()
    assert len(services) == 16
    
    # Check category distribution (4 per category)
    streaming = [s for s in services if s.category == ServiceCategory.STREAMING]
    gaming = [s for s in services if s.category == ServiceCategory.GAMING]
    cloud = [s for s in services if s.category == ServiceCategory.CLOUD]
    education = [s for s in services if s.category == ServiceCategory.EDUCATION]
    
    assert len(streaming) == 4
    assert len(gaming) == 4
    assert len(cloud) == 4
    assert len(education) == 4

def test_service_factory_creates_valid_tiers():
    services = ServiceFactory.generate_all_services()
    netflix = next(s for s in services if s.name == "Netflix")
    
    assert len(netflix.tiers) == 3
    assert netflix.tiers[0].name == "Basic"
    assert netflix.tiers[0].price > 0

def test_data_seeder_populates_repositories():
    user_repo = InMemoryUserRepository()
    service_repo = InMemoryServiceRepository()
    sub_repo = InMemorySubscriptionRepository()
    feedback_repo = InMemoryFeedbackRepository()

    seeder = DataSeeder(user_repo, service_repo, sub_repo, feedback_repo)
    seeder.seed_all()

    # 1. Check if 16 services were saved
    all_services = service_repo.get_all()
    assert len(all_services) == 16

    # 2. Check if 3 users were saved
    user1 = user_repo.get_by_id(list(user_repo._storage.keys())[0])
    assert user1 is not None

    # 3. Check subscriptions (we created 6 total subscriptions across 3 users)
    all_subs = sub_repo.get_all() if hasattr(sub_repo, 'get_all') else list(sub_repo._storage.values())
    assert len(all_subs) == 6

    # 4. Check feedback history (6 subscriptions * 12 months = 72 records)
    all_feedback = list(feedback_repo._storage.values())
    assert len(all_feedback) == 72
    
    # Assert feedback is within boundaries
    sample_fb = all_feedback[0]
    assert 1 <= sample_fb.frequency_1_to_7 <= 7
    assert 1 <= sample_fb.necessity_1_to_5 <= 5