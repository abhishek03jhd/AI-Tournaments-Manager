from __future__ import annotations

from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.domain.models import AlgorithmResult, Participant, TreeNode
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer

_ATTR_DELTA = 5
_ATTR_MIN = 1.0
_ATTR_MAX = 100.0


def _clamp(value: float) -> float:
    return max(_ATTR_MIN, min(_ATTR_MAX, value))


def _generate_neighbors(participant: Participant) -> list[Participant]:
    """Generate neighbors by varying each attribute by +/-5, clamped to [1, 100]."""
    neighbors: list[Participant] = []
    for key in participant.attributes:
        for delta in (+_ATTR_DELTA, -_ATTR_DELTA):
            new_attrs = dict(participant.attributes)
            new_attrs[key] = _clamp(new_attrs[key] + delta)
            neighbors.append(Participant(name=participant.name, attributes=new_attrs))
    return neighbors


def _mark_winning_path(node: TreeNode) -> None:
    """Mark nodes on the winning path from root to the winning leaf."""
    node.is_winning_path = True
    if not node.children:
        return
    for child in node.children:
        if child.value == node.value and not child.pruned:
            _mark_winning_path(child)
            return
    _mark_winning_path(node.children[0])


class MinimaxAlgorithm(Algorithm):
    """Minimax algorithm for two-player zero-sum game tree search."""

    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def evaluate(
        self,
        participant_a: Participant,
        participant_b: Participant,
        scorer: HeuristicScorer,
    ) -> AlgorithmResult:
        root, value = self._minimax(
            participant_a, participant_b, self.depth, is_maximizing=True, scorer=scorer
        )
        _mark_winning_path(root)

        score_a = scorer.score(participant_a)
        score_b = scorer.score(participant_b)

        if value >= 0:
            winner, loser = participant_a, participant_b
            winner_score, loser_score = score_a, score_b
        else:
            winner, loser = participant_b, participant_a
            winner_score, loser_score = score_b, score_a

        return AlgorithmResult(
            winner=winner,
            loser=loser,
            winner_score=winner_score,
            loser_score=loser_score,
            search_tree=root,
            search_path=None,
        )

    def _minimax(
        self,
        participant_a: Participant,
        participant_b: Participant,
        depth: int,
        is_maximizing: bool,
        scorer: HeuristicScorer,
    ) -> tuple[TreeNode, float]:
        score_a = scorer.score(participant_a)
        score_b = scorer.score(participant_b)
        node_value = score_a - score_b
        label = f"{participant_a.name} vs {participant_b.name}"

        if depth == 0:
            return TreeNode(label=label, value=node_value), node_value

        node = TreeNode(label=label, value=0.0)

        if is_maximizing:
            neighbors = _generate_neighbors(participant_a)
            best_value = float("-inf")
            for neighbor in neighbors:
                child, child_value = self._minimax(neighbor, participant_b, depth - 1, False, scorer)
                node.children.append(child)
                if child_value > best_value:
                    best_value = child_value
            node.value = best_value
            return node, best_value
        else:
            neighbors = _generate_neighbors(participant_b)
            best_value = float("inf")
            for neighbor in neighbors:
                child, child_value = self._minimax(participant_a, neighbor, depth - 1, True, scorer)
                node.children.append(child)
                if child_value < best_value:
                    best_value = child_value
            node.value = best_value
            return node, best_value
