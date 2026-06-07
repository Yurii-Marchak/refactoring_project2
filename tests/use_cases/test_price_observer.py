import pytest
from unittest.mock import Mock, call
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from src.models.subscription import UserSubscription
from src.services.use_cases.price_observer import PriceChangeSubject, UserNotificationObserver

def test_price_change_notifies_affected_users():

    service_id = uuid4()
    tier_name = "Premium"
    new_price = Decimal("15.99")
    
    user1_id = uuid4()
    user2_id = uuid4()
    user3_id = uuid4()

    subs = [
        UserSubscription(user_id=user1_id, service_id=service_id, tier_name=tier_name, start_date=datetime.now(), active=True),
        UserSubscription(user_id=user2_id, service_id=service_id, tier_name=tier_name, start_date=datetime.now(), active=True),
        UserSubscription(user_id=user3_id, service_id=service_id, tier_name="Basic", start_date=datetime.now(), active=True),
    ]

    mock_sub_repo = Mock()
    mock_sub_repo.get_all.return_value = subs
    
    mock_notif_service = Mock()

    subject = PriceChangeSubject()
    observer = UserNotificationObserver(mock_sub_repo, mock_notif_service)
    subject.attach(observer)


    subject.change_price(service_id, tier_name, new_price)


    assert mock_notif_service.send_notification.call_count == 2
    
    expected_message = f"Увага! Вартість вашого тарифу '{tier_name}' змінилася. Нова ціна: {new_price}."
    

    mock_notif_service.send_notification.assert_any_call(user1_id, expected_message)
    mock_notif_service.send_notification.assert_any_call(user2_id, expected_message)

def test_observer_detach():
    subject = PriceChangeSubject()
    observer = UserNotificationObserver(Mock(), Mock())
    
    subject.attach(observer)
    assert observer in subject._observers
    
    subject.detach(observer)
    assert observer not in subject._observers