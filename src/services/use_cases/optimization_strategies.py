from abc import ABC, abstractmethod
from typing import Optional
from decimal import Decimal
from dataclasses import dataclass

from src.models.subscription import UserSubscription
from src.models.service import Service

@dataclass
class OptimizationResult:
    """Internal DTO to pass results from strategies back to the Use Case."""
    action: str
    savings: Decimal

class IOptimizationStrategy(ABC):
    """
    Strategy interface for subscription optimization algorithms.
    """
    @abstractmethod
    def analyze(self, subscription: UserSubscription, service: Service, utility_score: float) -> Optional[OptimizationResult]:
        """
        Analyzes the subscription and returns an optimization recommendation if needed.
        Returns None if the subscription is highly useful and needs no optimization.
        """
        pass

class StreamingOptimizationStrategy(IOptimizationStrategy):
    """Strategy specific to streaming services (e.g., Netflix, Spotify)."""
    
    def analyze(self, subscription: UserSubscription, service: Service, utility_score: float) -> Optional[OptimizationResult]:
        # User is actively using it, no action needed
        if utility_score >= 70.0:
            return None
            
        current_tier = next((t for t in service.tiers if t.name == subscription.tier_name), None)
        current_price = current_tier.price if current_tier else Decimal('0.0')

        # If usage is extremely low, suggest cancelling
        if utility_score < 40.0:
            return OptimizationResult(
                action="Відмовитися від підписки і купувати фільми поштучно",
                savings=current_price
            )
        
        # If usage is moderate, suggest downgrading to a basic tier
        basic_tier = next((t for t in service.tiers if "basic" in t.name.lower() or t.price < current_price), None)
        if basic_tier and basic_tier.price < current_price:
            savings = current_price - basic_tier.price
            return OptimizationResult(
                action=f"Перейти на дешевший тариф '{basic_tier.name}'",
                savings=savings
            )
            
        return None

class GamingOptimizationStrategy(IOptimizationStrategy):
    """Strategy specific to gaming services (e.g., Xbox Game Pass)."""
    
    def analyze(self, subscription: UserSubscription, service: Service, utility_score: float) -> Optional[OptimizationResult]:
        if utility_score >= 60.0:
            return None
            
        current_tier = next((t for t in service.tiers if t.name == subscription.tier_name), None)
        current_price = current_tier.price if current_tier else Decimal('0.0')

        if utility_score < 30.0:
            return OptimizationResult(
                action="Відмовитися від підписки, оскільки ви майже не граєте",
                savings=current_price
            )
        else:
            return OptimizationResult(
                action="Призупинити підписку до виходу нових цікавих ігор",
                savings=current_price
            )

class DefaultOptimizationStrategy(IOptimizationStrategy):
    """Fallback strategy for unknown categories."""
    
    def analyze(self, subscription: UserSubscription, service: Service, utility_score: float) -> Optional[OptimizationResult]:
        if utility_score < 50.0:
            current_tier = next((t for t in service.tiers if t.name == subscription.tier_name), None)
            return OptimizationResult(
                action="Низький рівень використання. Розгляньте можливість скасування.",
                savings=current_tier.price if current_tier else Decimal('0.0')
            )
        return None