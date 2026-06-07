from typing import List
from src.models.feedback import UsageFeedback

class FuzzyUtilityCalculator:
    """
    Calculates a Utility Score (0.0 to 100.0) based on user feedback.
    Simulates Fuzzy Logic by applying weights to normalized crisp values.
    """

    def calculate_utility(self, feedbacks: List[UsageFeedback]) -> float:
        """
        Calculates the average utility score from a list of historical feedback.
        Returns 0.0 if there is no feedback history.
        """
        if not feedbacks:
            return 0.0

        total_score = 0.0
        for fb in feedbacks:
            # Normalize inputs to a 0.0 - 1.0 scale
            freq_norm = (fb.frequency_1_to_7 - 1) / 6.0
            nec_norm = (fb.necessity_1_to_5 - 1) / 4.0

            # Apply fuzzy rules via weighting:
            # Necessity represents a stronger personal tie (60% weight)
            # Frequency represents pure statistical usage (40% weight)
            score = (freq_norm * 0.4 + nec_norm * 0.6) * 100
            total_score += score

        return round(total_score / len(feedbacks), 2)