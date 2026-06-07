import pytest

from src.services.ports.user_repository import IUserRepository
from src.services.ports.service_repository import IServiceRepository
from src.services.ports.subscription_repository import ISubscriptionRepository
from src.services.ports.feedback_repository import IFeedbackRepository

def test_cannot_instantiate_iuser_repository():
    with pytest.raises(TypeError) as exc_info:
        IUserRepository()
    assert "Can't instantiate abstract class IUserRepository" in str(exc_info.value)

def test_cannot_instantiate_iservice_repository():
    with pytest.raises(TypeError) as exc_info:
        IServiceRepository()
    assert "Can't instantiate abstract class IServiceRepository" in str(exc_info.value)

def test_cannot_instantiate_isubscription_repository():
    with pytest.raises(TypeError) as exc_info:
        ISubscriptionRepository()
    assert "Can't instantiate abstract class ISubscriptionRepository" in str(exc_info.value)

def test_cannot_instantiate_ifeedback_repository():
    with pytest.raises(TypeError) as exc_info:
        IFeedbackRepository()
    assert "Can't instantiate abstract class IFeedbackRepository" in str(exc_info.value)
