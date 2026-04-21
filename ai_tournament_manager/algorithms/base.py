from __future__ import annotations

from abc import ABC, abstractmethod

from ai_tournament_manager.domain.models import AlgorithmResult, Participant
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer


class Algorithm(ABC):
    """Abstract base class for all tournament match algorithms."""

    @abstractmethod
    def evaluate(
        self,
        participant_a: Participant,
        participant_b: Participant,
        scorer: HeuristicScorer,
    ) -> AlgorithmResult:
        """Evaluate a match between two participants and return the result."""
        ...
