import pytest
from uuid import uuid4
from src.models.feedback import UsageFeedback
from src.storage.in_memory.feedback_repository import InMemoryFeedbackRepository

@pytest.fixture
def repo():
    return InMemoryFeedbackRepository()

def create_feedback(sub_id) -> UsageFeedback:
    return UsageFeedback(
        user_subscription_id=sub_id,
        month_year="2026-06",
        frequency_1_to_7=5,
        necessity_1_to_5=4,
        specific_metric={"hours_watched": 15}
    )

def test_save_and_get_history(repo):
    sub_id_1 = uuid4()
    sub_id_2 = uuid4()
    
    fb1 = create_feedback(sub_id_1)
    fb2 = create_feedback(sub_id_1)
    fb3 = create_feedback(sub_id_2)
    
    repo.save_feedback(fb1)
    repo.save_feedback(fb2)
    repo.save_feedback(fb3)
    
    history1 = repo.get_feedback_history(sub_id_1)
    assert len(history1) == 2
    
    history2 = repo.get_feedback_history(sub_id_2)
    assert len(history2) == 1
    assert history2[0].id == fb3.id

def test_get_history_empty(repo):
    history = repo.get_feedback_history(uuid4())
    assert len(history) == 0

def test_deep_copy_on_save(repo):
    sub_id = uuid4()
    fb = create_feedback(sub_id)
    repo.save_feedback(fb)
    
    fb.specific_metric["hours_watched"] = 30
    fetched = repo.get_feedback_history(sub_id)[0]
    
    assert fetched.specific_metric["hours_watched"] == 15

def test_deep_copy_on_get(repo):
    sub_id = uuid4()
    fb = create_feedback(sub_id)
    repo.save_feedback(fb)
    
    fetched = repo.get_feedback_history(sub_id)[0]
    fetched.specific_metric["new_metric"] = "test"
    
    second_fetch = repo.get_feedback_history(sub_id)[0]
    assert "new_metric" not in second_fetch.specific_metric
