from __future__ import annotations
import copy
import logging
from typing import Callable
from ai_tournament_manager.domain.enums import AlgorithmType, SeedingMode
from ai_tournament_manager.domain.models import Bracket, Match, MatchResult, Participant
from ai_tournament_manager.engine.bracket_generator import BracketGenerator
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer
from ai_tournament_manager.engine.simulation_engine import SimulationEngine

logger = logging.getLogger(__name__)


def _make_engine(algorithm_type: AlgorithmType, scorer: HeuristicScorer) -> SimulationEngine:
    from ai_tournament_manager.algorithms.minimax import MinimaxAlgorithm
    from ai_tournament_manager.algorithms.alpha_beta import AlphaBetaAlgorithm
    from ai_tournament_manager.algorithms.hill_climbing import HillClimbingAlgorithm
    algo = {
        AlgorithmType.MINIMAX: MinimaxAlgorithm,
        AlgorithmType.ALPHA_BETA: AlphaBetaAlgorithm,
        AlgorithmType.HILL_CLIMBING: HillClimbingAlgorithm,
    }[algorithm_type]()
    return SimulationEngine(algorithm=algo, scorer=scorer)


class TournamentController:
    def __init__(self) -> None:
        self._bracket: Bracket | None = None
        self._original_bracket: Bracket | None = None
        self._engine: SimulationEngine | None = None
        self._algorithm_type: AlgorithmType = AlgorithmType.MINIMAX
        self._scorer = HeuristicScorer()
        self._on_match_complete: list[Callable[[MatchResult], None]] = []
        self._on_tournament_complete: list[Callable[[Participant], None]] = []

    def create_tournament(self, participants, algorithm=AlgorithmType.MINIMAX, seeding=SeedingMode.RANDOM) -> Bracket:
        for p in participants:
            self._scorer.score(p)
        self._algorithm_type = algorithm
        self._engine = _make_engine(algorithm, self._scorer)
        self._bracket = BracketGenerator().generate(participants, seeding)
        self._original_bracket = copy.deepcopy(self._bracket)
        return self._bracket

    def step(self) -> MatchResult | None:
        if not self._bracket or self._bracket.is_complete():
            return None
        pending = self._bracket.pending_matches()
        if not pending:
            return None
        match = pending[0]
        result = self._engine.resolve_match(match)
        self._advance_winner(match)
        for cb in self._on_match_complete:
            cb(result)
        if self._bracket.is_complete():
            self._bracket.champion = result.algorithm_result.winner
            for cb in self._on_tournament_complete:
                cb(self._bracket.champion)
        return result

    def run_all(self) -> None:
        while self._bracket and not self._bracket.is_complete():
            self.step()

    def reset(self) -> None:
        if self._original_bracket:
            self._bracket = copy.deepcopy(self._original_bracket)

    def export_results(self, path: str) -> None:
        from ai_tournament_manager.export.results_exporter import ResultsExporter
        if not self._bracket:
            raise RuntimeError("No tournament to export.")
        ResultsExporter().export(self._bracket, path)

    def register_on_match_complete(self, cb: Callable[[MatchResult], None]) -> None:
        self._on_match_complete.append(cb)

    def register_on_tournament_complete(self, cb: Callable[[Participant], None]) -> None:
        self._on_tournament_complete.append(cb)

    def _advance_winner(self, match: Match) -> None:
        if not self._bracket or not match.winner:
            return
        next_round_idx = match.round_number
        if next_round_idx >= len(self._bracket.rounds):
            return
        next_round = self._bracket.rounds[next_round_idx]
        curr_round = self._bracket.rounds[match.round_number - 1]
        match_idx = curr_round.matches.index(match)
        next_match = next_round.matches[match_idx // 2]
        if match_idx % 2 == 0:
            next_match.participant_a = match.winner
        else:
            next_match.participant_b = match.winner

    @property
    def bracket(self) -> Bracket | None:
        return self._bracket
