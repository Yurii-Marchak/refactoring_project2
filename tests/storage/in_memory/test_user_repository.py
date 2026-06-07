import pytest
from uuid import uuid4
from src.models.user import User
from src.storage.in_memory.user_repository import InMemoryUserRepository

@pytest.fixture
def repo():
    return InMemoryUserRepository()

def test_save_and_get_by_id(repo):
    user = User(email="test@example.com", preferences={"theme": "dark"})
    saved_user = repo.save(user)
    
    assert saved_user.id == user.id
    assert saved_user.email == "test@example.com"
    
    fetched_user = repo.get_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == user.email

def test_get_by_id_not_found(repo):
    fetched_user = repo.get_by_id(uuid4())
    assert fetched_user is None

def test_update_existing_user(repo):
    user = User(email="update@example.com")
    repo.save(user)
    
    user.email = "updated@example.com"
    user.preferences = {"lang": "uk"}
    
    updated_user = repo.update(user)
    assert updated_user.email == "updated@example.com"
    assert updated_user.preferences == {"lang": "uk"}
    
    fetched_user = repo.get_by_id(user.id)
    assert fetched_user.email == "updated@example.com"
    assert fetched_user.preferences == {"lang": "uk"}

def test_update_non_existent_user(repo):
    user = User(email="notfound@example.com")
    with pytest.raises(ValueError, match=f"User with id {user.id} not found."):
        repo.update(user)

def test_deep_copy_on_save(repo):
    user = User(email="copy@example.com", preferences={"items": [1, 2, 3]})
    repo.save(user)
    
    user.preferences["items"].append(4)
    fetched_user = repo.get_by_id(user.id)
    
    assert 4 not in fetched_user.preferences["items"]

def test_deep_copy_on_get(repo):
    user = User(email="copyget@example.com", preferences={"items": [1, 2]})
    repo.save(user)
    
    fetched_user = repo.get_by_id(user.id)
    fetched_user.preferences["items"].append(3)
    
    second_fetch = repo.get_by_id(user.id)
    assert 3 not in second_fetch.preferences["items"]
