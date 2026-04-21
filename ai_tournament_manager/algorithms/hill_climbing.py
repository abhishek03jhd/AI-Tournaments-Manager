from __future__ import annotations

from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.algorithms.minimax import _generate_neighbors
from ai_tournament_manager.domain.models import AlgorithmResult, Participant, SearchState
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer


def _hill_climb(participant: Participant, scorer: HeuristicScorer) -> list[SearchState]:
    """Run hill climbing for a single participant; return the search path."""
    path: list[SearchState] = []
    current = participant
    current_value = scorer.score(current)

    while True:
        path.append(SearchState(participant=current, heuristic_value=current_value))
        neighbors = _generate_neighbors(current)
        best_neighbor = None
        best_value = current_value

        for neighbor in neighbors:
            val = scorer.score(neighbor)
            if val > best_value:
                best_value = val
                best_neighbor = neighbor

        if best_neighbor is None:
            path[-1].is_local_max = True
            break

        current = best_neighbor
        current_value = best_value

    return path


class HillClimbingAlgorithm(Algorithm):
    """Hill Climbing — independently optimises each participant's attributes."""

    def evaluate(
        self,
        participant_a: Participant,
        participant_b: Participant,
        scorer: HeuristicScorer,
    ) -> AlgorithmResult:
        path_a = _hill_climb(participant_a, scorer)
        path_b = _hill_climb(participant_b, scorer)

        terminal_a = path_a[-1].heuristic_value
        terminal_b = path_b[-1].heuristic_value

        if terminal_a > terminal_b:
            winner, loser = participant_a, participant_b
            winner_score, loser_score = terminal_a, terminal_b
        elif terminal_b > terminal_a:
            winner, loser = participant_b, participant_a
            winner_score, loser_score = terminal_b, terminal_a
        else:
            winner = scorer.tiebreak(participant_a, participant_b)
            loser = participant_b if winner is participant_a else participant_a
            winner_score, loser_score = terminal_a, terminal_b

        return AlgorithmResult(
            winner=winner, loser=loser,
            winner_score=winner_score, loser_score=loser_score,
            search_tree=None, search_path=path_a + path_b,
        )
