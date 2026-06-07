import secrets
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List

from src.models.service import Service, ServiceCategory, SubscriptionTier
from src.models.user import User
from src.models.subscription import UserSubscription
from src.models.feedback import UsageFeedback
from src.services.ports.user_repository import IUserRepository
from src.services.ports.service_repository import IServiceRepository
from src.services.ports.subscription_repository import ISubscriptionRepository
from src.services.ports.feedback_repository import IFeedbackRepository

class ServiceFactory:
    """
    Factory for generating the required 16 core services across 4 categories.
    """
    @staticmethod
    def generate_all_services() -> List[Service]:
        services = []
        
        # 1. Стрімінгові сервіси [cite: 63]
        streaming_data = [
            ("Netflix", [("Basic", "5.99"), ("Standard", "10.99"), ("Premium", "15.99")]),
            ("Spotify", [("Individual", "4.99"), ("Duo", "6.49"), ("Family", "7.99")]),
            ("YouTube Premium", [("Student", "3.99"), ("Individual", "7.99"), ("Family", "11.99")]),
            ("Megogo", [("Легка", "3.00"), ("Максимальна", "8.00"), ("Спорт", "6.00")])
        ]
        for name, tiers in streaming_data:
            services.append(ServiceFactory._build_service(name, ServiceCategory.STREAMING, tiers))

        # 2. Програми та хмарні сховища [cite: 64]
        cloud_data = [
            ("Google One", [("Basic 100GB", "1.99"), ("Standard 200GB", "2.99"), ("Premium 2TB", "9.99")]),
            ("iCloud", [("50GB", "0.99"), ("200GB", "2.99"), ("2TB", "9.99")]),
            ("Adobe Creative Cloud", [("Photography", "9.99"), ("All Apps", "54.99")]),
            ("Microsoft 365", [("Personal", "6.99"), ("Family", "9.99")])
        ]
        for name, tiers in cloud_data:
            services.append(ServiceFactory._build_service(name, ServiceCategory.CLOUD, tiers))

        # 3. Ігри [cite: 65]
        gaming_data = [
            ("Xbox Game Pass", [("Core", "9.99"), ("PC", "9.99"), ("Ultimate", "16.99")]),
            ("PlayStation Plus", [("Essential", "9.99"), ("Extra", "14.99"), ("Premium", "17.99")]),
            ("EA Play", [("Standard", "4.99"), ("Pro", "14.99")]),
            ("Nintendo Switch Online", [("Individual", "3.99"), ("Family", "7.99")])
        ]
        for name, tiers in gaming_data:
            services.append(ServiceFactory._build_service(name, ServiceCategory.GAMING, tiers))

        # 4. Освіта та професійні інструменти [cite: 66]
        edu_data = [
            ("ChatGPT", [("Plus", "20.00"), ("Team", "25.00")]),
            ("Duolingo", [("Super", "6.99"), ("Super Family", "9.99")]),
            ("Coursera", [("Plus Monthly", "59.00"), ("Plus Annual", "399.00")]),
            ("GitHub Copilot", [("Individual", "10.00"), ("Business", "19.00")])
        ]
        for name, tiers in edu_data:
            services.append(ServiceFactory._build_service(name, ServiceCategory.EDUCATION, tiers))

        return services

    @staticmethod
    def _build_service(name: str, category: ServiceCategory, tiers_data: list) -> Service:
        tiers = [SubscriptionTier(name=t_name, price=Decimal(t_price)) for t_name, t_price in tiers_data]
        return Service(id=uuid4(), name=name, category=category, tiers=tiers)

class DataSeeder:
    """
    Seeds the in-memory repositories with services, users, subscriptions, and feedback history.
    """
    def __init__(
        self,
        user_repo: IUserRepository,
        service_repo: IServiceRepository,
        sub_repo: ISubscriptionRepository,
        feedback_repo: IFeedbackRepository
    ):
        self.user_repo = user_repo
        self.service_repo = service_repo
        self.sub_repo = sub_repo
        self.feedback_repo = feedback_repo

    def seed_all(self):
        # 1. Seed Services
        services = ServiceFactory.generate_all_services()
        for service in services:
            self.service_repo.save(service)

        # 2. Seed Users
        users = [
            User(id=uuid4(), email="active_geek@example.com", preferences={"theme": "dark"}),
            User(id=uuid4(), email="forgetful_payer@example.com", preferences={"theme": "light"}),
            User(id=uuid4(), email="balanced_user@example.com", preferences={})
        ]
        for user in users:
            self.user_repo.save(user)

        # 3. Seed Subscriptions and Feedback for 12 months
        months_history = self._generate_last_12_months()
        start_date = datetime.now() - timedelta(days=365)

        # User 1: High activity (uses everything constantly)
        self._create_subscription_with_feedback(
            user_id=users[0].id, service=services[0], tier_name="Premium",  # Netflix
            start_date=start_date, months=months_history, freq_range=(5, 7), nec_range=(4, 5)
        )
        self._create_subscription_with_feedback(
            user_id=users[0].id, service=services[12], tier_name="Plus",    # ChatGPT
            start_date=start_date, months=months_history, freq_range=(6, 7), nec_range=(5, 5)
        )

        # User 2: Low activity (pays but never uses - perfect for cancellation logic)
        self._create_subscription_with_feedback(
            user_id=users[1].id, service=services[8], tier_name="Ultimate", # Xbox
            start_date=start_date, months=months_history, freq_range=(1, 2), nec_range=(1, 2)
        )
        self._create_subscription_with_feedback(
            user_id=users[1].id, service=services[2], tier_name="Premium",  # YouTube
            start_date=start_date, months=months_history, freq_range=(1, 3), nec_range=(2, 3)
        )

        # User 3: Mixed activity
        self._create_subscription_with_feedback(
            user_id=users[2].id, service=services[1], tier_name="Individual", # Spotify (high usage)
            start_date=start_date, months=months_history, freq_range=(6, 7), nec_range=(5, 5)
        )
        self._create_subscription_with_feedback(
            user_id=users[2].id, service=services[4], tier_name="Standard 200GB", # Google One (med usage)
            start_date=start_date, months=months_history, freq_range=(3, 4), nec_range=(3, 4)
        )

    def _generate_last_12_months(self) -> List[str]:
        months = []
        current = datetime.now()
        for i in range(12):
            target_month = current - timedelta(days=30 * i)
            months.append(target_month.strftime("%Y-%m"))
        return months[::-1] # Reverse to chronological order

    def _create_subscription_with_feedback(
        self, user_id, service, tier_name, start_date, months, freq_range, nec_range
    ):
        sub = UserSubscription(
            id=uuid4(), user_id=user_id, service_id=service.id, 
            tier_name=tier_name, start_date=start_date, active=True
        )
        self.sub_repo.add_subscription(sub)

        for month in months:
            feedback = UsageFeedback(
                id=uuid4(),
                user_subscription_id=sub.id,
                month_year=month,
                # Використовуємо secrets.choice(range(start, end + 1)) замість randint
                frequency_1_to_7=secrets.choice(range(freq_range[0], freq_range[1] + 1)),
                necessity_1_to_5=secrets.choice(range(nec_range[0], nec_range[1] + 1))
            )
            self.feedback_repo.save_feedback(feedback)