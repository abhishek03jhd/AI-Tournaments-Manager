from __future__ import annotations
from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.algorithms.minimax import _generate_neighbors
from ai_tournament_manager.domain.models import AlgorithmResult, Participant, SearchState
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer


def _hill_climb(participant: Participant, scorer: HeuristicScorer) -> list[SearchState]:
    path: list[SearchState] = []
    current, current_value = participant, scorer.score(participant)
    while True:
        path.append(SearchState(participant=current, heuristic_value=current_value))
        best_neighbor, best_value = None, current_value
        for neighbor in _generate_neighbors(current):
            val = scorer.score(neighbor)
            if val > best_value:
                best_value, best_neighbor = val, neighbor
        if best_neighbor is None:
            path[-1].is_local_max = True
            break
        current, current_value = best_neighbor, best_value
    return path


class HillClimbingAlgorithm(Algorithm):
    def evaluate(self, participant_a, participant_b, scorer) -> AlgorithmResult:
        path_a = _hill_climb(participant_a, scorer)
        path_b = _hill_climb(participant_b, scorer)
        ta, tb = path_a[-1].heuristic_value, path_b[-1].heuristic_value
        if ta > tb:
            winner, loser, ws, ls = participant_a, participant_b, ta, tb
        elif tb > ta:
            winner, loser, ws, ls = participant_b, participant_a, tb, ta
        else:
            winner = scorer.tiebreak(participant_a, participant_b)
            loser = participant_b if winner is participant_a else participant_a
            ws, ls = ta, tb
        return AlgorithmResult(winner=winner, loser=loser, winner_score=ws, loser_score=ls,
                               search_tree=None, search_path=path_a + path_b)
