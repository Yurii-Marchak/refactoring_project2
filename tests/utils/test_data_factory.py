import re
from uuid import uuid4
from datetime import datetime
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


    all_services = service_repo.get_all()
    assert len(all_services) == 16


    user1 = user_repo.get_by_id(list(user_repo._storage.keys())[0])
    assert user1 is not None


    all_subs = sub_repo.get_all() if hasattr(sub_repo, 'get_all') else list(sub_repo._storage.values())
    assert len(all_subs) == 6


    all_feedback = list(feedback_repo._storage.values())
    assert len(all_feedback) == 72
    

    sample_fb = all_feedback[0]
    assert 1 <= sample_fb.frequency_1_to_7 <= 7
    assert 1 <= sample_fb.necessity_1_to_5 <= 5

def test_generate_last_12_months_format_and_length():
    """Перевірка, що метод генерує рівно 12 дат у форматі YYYY-MM."""
    seeder = DataSeeder(
        InMemoryUserRepository(), 
        InMemoryServiceRepository(), 
        InMemorySubscriptionRepository(), 
        InMemoryFeedbackRepository()
    )
    
    months = seeder._generate_last_12_months()
    
    assert len(months) == 12
    

    pattern = re.compile(r"^\d{4}-\d{2}$")
    for month in months:
        assert pattern.match(month) is not None, f"Формат місяця {month} не відповідає YYYY-MM"

def test_data_seeder_safe_multiple_calls():
    """
    Перевірка, що Seeder не падає при повторному виклику.
    Оскільки ми щоразу генеруємо нові UUID, він просто додасть нові записи,
    але головне — система не повинна видавати винятків.
    """
    user_repo = InMemoryUserRepository()
    service_repo = InMemoryServiceRepository()
    sub_repo = InMemorySubscriptionRepository()
    feedback_repo = InMemoryFeedbackRepository()

    seeder = DataSeeder(user_repo, service_repo, sub_repo, feedback_repo)


    seeder.seed_all()
    users_count_first = len(user_repo._storage)
    

    try:
        seeder.seed_all()
    except Exception as e:
        pytest.fail(f"Seeder впав при спробі повторного запуску: {e}")
        

    users_count_second = len(user_repo._storage)
    assert users_count_second > users_count_first

def test_create_subscription_with_feedback_internal_logic():
    """
    Пряме тестування внутрішнього методу для збільшення покриття рядків.
    Перевіряємо, чи правильно створюється підписка і прив'язуються відгуки.
    """
    user_repo = InMemoryUserRepository()
    service_repo = InMemoryServiceRepository()
    sub_repo = InMemorySubscriptionRepository()
    feedback_repo = InMemoryFeedbackRepository()

    seeder = DataSeeder(user_repo, service_repo, sub_repo, feedback_repo)
    services = ServiceFactory.generate_all_services()
    test_user_id = uuid4()
    

    test_months = ["2026-03", "2026-04", "2026-05"]
    seeder._create_subscription_with_feedback(
        user_id=test_user_id,
        service=services[0],
        tier_name="Premium",
        start_date=datetime.now(),
        months=test_months,
        freq_range=(1, 7),
        nec_range=(1, 5)
    )
    

    subs = sub_repo.get_user_subscriptions(test_user_id)
    assert len(subs) == 1
    assert subs[0].tier_name == "Premium"
    

    feedbacks = feedback_repo.get_feedback_history(subs[0].id)
    assert len(feedbacks) == 3