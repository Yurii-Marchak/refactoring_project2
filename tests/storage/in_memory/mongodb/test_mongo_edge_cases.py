import pytest
import mongomock
from uuid import uuid4
from src.models.user import User
from src.models.service import Service, ServiceCategory, SubscriptionTier
from src.storage.mongodb.user_repository import MongoUserRepository
from src.storage.mongodb.service_repository import MongoServiceRepository

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    return client.edge_cases_db

# ==========================================
# TEST BLOCKS: MongoDB Edge Cases
# ==========================================

def test_update_nonexistent_user_raises_error(mock_db):
    """1. Спроба оновити користувача, якого не існує в колекції."""
    repo = MongoUserRepository(mock_db.users)
    user = User(id=uuid4(), email="ghost@test.com", preferences={})
    
    with pytest.raises(ValueError, match="not found"):
        repo.update(user)

def test_get_by_category_no_services_returns_empty(mock_db):
    """2. Вибірка категорії, в якій немає жодного сервісу."""
    repo = MongoServiceRepository(mock_db.services)
    # Запитуємо категорію, якої немає в БД
    results = repo.get_by_category(ServiceCategory.GAMING)
    assert results == []
    assert isinstance(results, list)

def test_get_by_id_returns_none_for_missing(mock_db):
    """3. get_by_id має повертати None, а не падати, якщо ID відсутній."""
    repo = MongoUserRepository(mock_db.users)
    result = repo.get_by_id(uuid4())
    assert result is None


def test_get_by_category_with_wrong_type(mock_db):
    """5. Перевірка роботи з некоректним типом категорії."""
    repo = MongoServiceRepository(mock_db.services)
    assert repo.get_by_category("NOT_A_CATEGORY") == []

def test_update_user_partial_data(mock_db):
    """6. Перевірка, що update працює коректно при збереженні об'єкта."""
    repo = MongoUserRepository(mock_db.users)
    uid = uuid4()
    user = User(id=uid, email="orig@test.com", preferences={})
    repo.save(user)
    
    user.email = "new@test.com"
    repo.update(user)
    assert repo.get_by_id(uid).email == "new@test.com"

def test_repository_handles_empty_collection(mock_db):
    """7. Робота з порожньою колекцією сервісів."""
    repo = MongoServiceRepository(mock_db.services)
    assert repo.get_all() == []

def test_service_repo_filter_logic(mock_db):
    """8. Фільтрація: зберігаємо 2 сервіси, отримуємо 1 за категорією."""
    repo = MongoServiceRepository(mock_db.services)
    s1 = Service(id=uuid4(), name="S1", category=ServiceCategory.CLOUD, tiers=[])
    s2 = Service(id=uuid4(), name="S2", category=ServiceCategory.STREAMING, tiers=[])
    repo.save(s1)
    repo.save(s2)
    
    results = repo.get_by_category(ServiceCategory.CLOUD)
    assert len(results) == 1
    assert results[0].name == "S1"

def test_user_repo_id_as_string_vs_uuid(mock_db):
    """9. Перевірка, чи працює пошук, якщо передати UUID, а не str."""
    repo = MongoUserRepository(mock_db.users)
    uid = uuid4()
    user = User(id=uid, email="test@test.com", preferences={})
    repo.save(user)
    
    # Передаємо об'єкт UUID, а не рядок
    assert repo.get_by_id(uid) is not None

def test_complex_preferences_persistence(mock_db):
    """10. Перевірка, що вкладені словники в Preferences зберігаються коректно."""
    repo = MongoUserRepository(mock_db.users)
    prefs = {"notifications": {"email": True, "sms": False}, "lang": "uk"}
    user = User(id=uuid4(), email="test@test.com", preferences=prefs)
    repo.save(user)
    
    fetched = repo.get_by_id(user.id)
    assert fetched.preferences["notifications"]["email"] is True

def test_service_with_multiple_tiers_persistence(mock_db):
    """11. Перевірка, що вкладений список тарифів зберігається коректно."""
    repo = MongoServiceRepository(mock_db.services)
    tiers = [
        SubscriptionTier(name="T1", price=10.0),
        SubscriptionTier(name="T2", price=20.0)
    ]
    s = Service(id=uuid4(), name="MultiTier", category=ServiceCategory.GAMING, tiers=tiers)
    repo.save(s)
    
    fetched = repo.get_all()[0]
    assert len(fetched.tiers) == 2
    assert fetched.tiers[1].name == "T2"

def test_update_non_existent_field_in_db(mock_db):
    """12. Перевірка, що MongoDB не видаляє поля, якщо ми їх не вказали в Pydantic (але тут Pydantic все контролює)."""
    repo = MongoUserRepository(mock_db.users)
    uid = uuid4()
    repo.save(User(id=uid, email="test@test.com", preferences={}))
    
    # Додамо поле вручну через драйвер, яке Pydantic не знає
    mock_db.users.update_one({"id": str(uid)}, {"$set": {"extra_field": "surprise"}})
    
    # Репозиторій має все одно прочитати об'єкт (Pydantic просто проігнорує extra_field)
    user = repo.get_by_id(uid)
    assert user.id == uid

def test_repository_save_returns_object(mock_db):
    """13. Перевірка, що метод save повертає переданий об'єкт."""
    repo = MongoUserRepository(mock_db.users)
    user = User(id=uuid4(), email="return@test.com", preferences={})
    returned = repo.save(user)
    assert returned == user

def test_get_by_category_case_sensitivity(mock_db):
    """14. Перевірка (або демонстрація) чутливості до регістру."""
    repo = MongoServiceRepository(mock_db.services)
    # Зберігаємо категорію 'cloud'
    repo.save(Service(id=uuid4(), name="CloudSvc", category=ServiceCategory.CLOUD, tiers=[]))
    # MongoDB зазвичай чутлива до регістру
    assert repo.get_by_category("CLOUD") == []

def test_save_feedback_persistence(mock_db):
    """15. Перевірка збереження відгуку."""
    from src.storage.mongodb.feedback_repository import MongoFeedbackRepository
    from src.models.feedback import UsageFeedback
    
    repo = MongoFeedbackRepository(mock_db.feedbacks)
    fb = UsageFeedback(user_subscription_id=uuid4(), month_year="2026-06", frequency_1_to_7=1, necessity_1_to_5=1)
    repo.save_feedback(fb)
    
    assert mock_db.feedbacks.count_documents({}) == 1