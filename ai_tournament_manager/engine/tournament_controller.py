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


def _algorithm_for_type(algorithm_type: AlgorithmType, scorer: HeuristicScorer) -> SimulationEngine:
    from ai_tournament_manager.algorithms.minimax import MinimaxAlgorithm
    from ai_tournament_manager.algorithms.alpha_beta import AlphaBetaAlgorithm
    from ai_tournament_manager.algorithms.hill_climbing import HillClimbingAlgorithm

    if algorithm_type == AlgorithmType.MINIMAX:
        algo = MinimaxAlgorithm()
    elif algorithm_type == AlgorithmType.ALPHA_BETA:
        algo = AlphaBetaAlgorithm()
    else:
        algo = HillClimbingAlgorithm()
    return SimulationEngine(algorithm=algo, scorer=scorer)


class TournamentController:
    """Orchestrates the full tournament lifecycle."""

    def __init__(self) -> None:
        self._bracket: Bracket | None = None
        self._original_bracket: Bracket | None = None
        self._engine: SimulationEngine | None = None
        self._algorithm_type: AlgorithmType = AlgorithmType.MINIMAX
        self._scorer = HeuristicScorer()
        self._on_match_complete: list[Callable[[MatchResult], None]] = []
        self._on_tournament_complete: list[Callable[[Participant], None]] = []

    # ------------------------------------------------------------------ setup

    def create_tournament(
        self,
        participants: list[Participant],
        algorithm: AlgorithmType = AlgorithmType.MINIMAX,
        seeding: SeedingMode = SeedingMode.RANDOM,
    ) -> Bracket:
        # Score all participants up front
        for p in participants:
            self._scorer.score(p)

        self._algorithm_type = algorithm
        self._engine = _algorithm_for_type(algorithm, self._scorer)

        generator = BracketGenerator()
        self._bracket = generator.generate(participants, seeding)
        # Deep-copy for reset
        self._original_bracket = copy.deepcopy(self._bracket)
        return self._bracket

    # ---------------------------------------------------------------- control

    def step(self) -> MatchResult | None:
        """Advance the simulation by one match. Returns None if complete."""
        if self._bracket is None or self._bracket.is_complete():
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
        """Simulate all remaining matches sequentially."""
        while self._bracket and not self._bracket.is_complete():
            self.step()

    def reset(self) -> None:
        """Return the bracket to its initial pre-simulation state."""
        if self._original_bracket is not None:
            self._bracket = copy.deepcopy(self._original_bracket)

    def export_results(self, path: str) -> None:
        from ai_tournament_manager.export.results_exporter import ResultsExporter
        if self._bracket is None:
            raise RuntimeError("No tournament to export.")
        ResultsExporter().export(self._bracket, path)

    # ------------------------------------------------------------ callbacks

    def register_on_match_complete(self, callback: Callable[[MatchResult], None]) -> None:
        self._on_match_complete.append(callback)

    def register_on_tournament_complete(self, callback: Callable[[Participant], None]) -> None:
        self._on_tournament_complete.append(callback)

    # ------------------------------------------------------------ helpers

    def _advance_winner(self, match: Match) -> None:
        """Place the match winner into the correct slot of the next round."""
        if self._bracket is None or match.winner is None:
            return
        next_round_idx = match.round_number  # rounds are 1-indexed; next round index = round_number
        if next_round_idx >= len(self._bracket.rounds):
            return  # Final — no next round
        next_round = self._bracket.rounds[next_round_idx]
        # Match index within its round (0-based)
        current_round = self._bracket.rounds[match.round_number - 1]
        match_idx = current_round.matches.index(match)
        next_match_idx = match_idx // 2
        if next_match_idx >= len(next_round.matches):
            return
        next_match = next_round.matches[next_match_idx]
        if match_idx % 2 == 0:
            next_match.participant_a = match.winner
        else:
            next_match.participant_b = match.winner

    @property
    def bracket(self) -> Bracket | None:
        return self._bracket

    @property
    def algorithm_type(self) -> AlgorithmType:
        return self._algorithm_type
