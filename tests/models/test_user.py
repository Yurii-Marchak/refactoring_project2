import pytest
from uuid import UUID
from pydantic import ValidationError
from src.models.user import User

def test_create_user_success():
    user = User(email="test@example.com", preferences={"theme": "dark"})
    assert isinstance(user.id, UUID)
    assert user.email == "test@example.com"
    assert user.preferences == {"theme": "dark"}

def test_create_user_default_preferences():
    user = User(email="test@example.com")
    assert user.preferences == {}

def test_create_user_missing_email():
    with pytest.raises(ValidationError):
        User(preferences={})
