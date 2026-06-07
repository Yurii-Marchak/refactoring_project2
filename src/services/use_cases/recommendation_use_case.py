from typing import List, Dict
from uuid import UUID

from src.models.recommendation import Recommendation
from src.models.service import ServiceCategory
from src.services.ports.user_repository import IUserRepository
from src.services.ports.subscription_repository import ISubscriptionRepository
from src.services.ports.service_repository import IServiceRepository
from src.services.ports.feedback_repository import IFeedbackRepository
from src.services.use_cases.fuzzy_logic import FuzzyUtilityCalculator
from src.services.use_cases.optimization_strategies import (
    IOptimizationStrategy,
    StreamingOptimizationStrategy,
    GamingOptimizationStrategy,
    DefaultOptimizationStrategy
)

class GenerateRecommendationsUseCase:
    """
    Main orchestrator for generating subscription optimization plans.
    """
    def __init__(
        self,
        user_repo: IUserRepository,
        subscription_repo: ISubscriptionRepository,
        service_repo: IServiceRepository,
        feedback_repo: IFeedbackRepository,
        fuzzy_calculator: FuzzyUtilityCalculator
    ):
        # Inject dependencies
        self.user_repo = user_repo
        self.subscription_repo = subscription_repo
        self.service_repo = service_repo
        self.feedback_repo = feedback_repo
        self.fuzzy_calculator = fuzzy_calculator
        
        # Strategy mapping based on category
        self.strategies: Dict[ServiceCategory, IOptimizationStrategy] = {
            ServiceCategory.STREAMING: StreamingOptimizationStrategy(),
            ServiceCategory.GAMING: GamingOptimizationStrategy(),
        }
        self.default_strategy = DefaultOptimizationStrategy()

    def execute(self, user_id: UUID | str) -> List[Recommendation]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found.")

        user_subs = self.subscription_repo.get_user_subscriptions(user_id)
        active_subs = [sub for sub in user_subs if sub.active]
        
        recommendations: List[Recommendation] = []
        
        # Cache services to minimize DB calls
        all_services = {str(s.id): s for s in self.service_repo.get_all()}

        for sub in active_subs:
            service = all_services.get(str(sub.service_id))
            if not service:
                continue
                
            # 1. Gather historical data
            feedback_history = self.feedback_repo.get_feedback_history(sub.id)
            
            # 2. Run Fuzzy Logic rules
            utility_score = self.fuzzy_calculator.calculate_utility(feedback_history)
            
            # 3. Select and execute the proper strategy
            strategy = self.strategies.get(service.category, self.default_strategy)
            opt_result = strategy.analyze(sub, service, utility_score)
            
            # 4. Compile the final report if an action was suggested
            if opt_result:
                recommendations.append(Recommendation(
                    user_subscription_id=sub.id,
                    service_name=service.name,
                    current_tier=sub.tier_name,
                    utility_score=utility_score,
                    suggested_action=opt_result.action,
                    estimated_monthly_savings=opt_result.savings
                ))
                
        return recommendations