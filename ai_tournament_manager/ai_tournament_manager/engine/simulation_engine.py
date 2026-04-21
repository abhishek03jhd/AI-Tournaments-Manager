from __future__ import annotations
import logging
import threading
from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.domain.models import Match, MatchResult
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer

logger = logging.getLogger(__name__)
MATCH_TIMEOUT_SECONDS = 2.0


class SimulationTimeoutError(Exception):
    pass


class SimulationEngine:
    def __init__(self, algorithm: Algorithm, scorer: HeuristicScorer) -> None:
        self.algorithm = algorithm
        self.scorer = scorer

    def resolve_match(self, match: Match) -> MatchResult:
        if match.participant_a is None or match.participant_b is None:
            raise ValueError(f"Match {match.id} has unfilled participant slots.")
        result_holder: list = []
        error_holder: list = []

        def _run():
            try:
                result_holder.append(self.algorithm.evaluate(match.participant_a, match.participant_b, self.scorer))
            except Exception as exc:
                error_holder.append(exc)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=MATCH_TIMEOUT_SECONDS)
        if t.is_alive():
            raise SimulationTimeoutError(f"Match {match.id} timed out after {MATCH_TIMEOUT_SECONDS}s.")
        if error_holder:
            raise error_holder[0]
        algo_result = result_holder[0]
        match.winner = algo_result.winner
        match.algorithm_result = algo_result
        return MatchResult(match=match, algorithm_result=algo_result)
