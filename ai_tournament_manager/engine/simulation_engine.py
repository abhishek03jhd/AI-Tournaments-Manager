from __future__ import annotations

import logging
import threading

from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.domain.models import Match, MatchResult
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer

logger = logging.getLogger(__name__)

MATCH_TIMEOUT_SECONDS = 2.0


class SimulationTimeoutError(Exception):
    """Raised when an algorithm evaluation exceeds the allowed time."""


class SimulationEngine:
    """Resolves a single match using the configured algorithm."""

    def __init__(self, algorithm: Algorithm, scorer: HeuristicScorer) -> None:
        self.algorithm = algorithm
        self.scorer = scorer

    def resolve_match(self, match: Match) -> MatchResult:
        """Evaluate the match and return a MatchResult.

        Raises:
            SimulationTimeoutError: If evaluation exceeds 2 seconds.
            ValueError: If either participant slot is None.
        """
        if match.participant_a is None or match.participant_b is None:
            raise ValueError(f"Match {match.id} has unfilled participant slots.")

        result_holder: list = []
        error_holder: list = []

        def _run() -> None:
            try:
                result_holder.append(
                    self.algorithm.evaluate(match.participant_a, match.participant_b, self.scorer)
                )
            except Exception as exc:  # noqa: BLE001
                error_holder.append(exc)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=MATCH_TIMEOUT_SECONDS)

        if thread.is_alive():
            raise SimulationTimeoutError(
                f"Algorithm evaluation for match {match.id} exceeded {MATCH_TIMEOUT_SECONDS}s."
            )

        if error_holder:
            logger.exception("Unexpected error during match %s", match.id, exc_info=error_holder[0])
            raise error_holder[0]

        algo_result = result_holder[0]
        match.winner = algo_result.winner
        match.algorithm_result = algo_result
        return MatchResult(match=match, algorithm_result=algo_result)
