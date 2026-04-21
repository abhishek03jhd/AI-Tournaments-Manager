from __future__ import annotations
from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.domain.models import AlgorithmResult, Participant, TreeNode
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer

_ATTR_DELTA = 5
_ATTR_MIN, _ATTR_MAX = 1.0, 100.0


def _clamp(v: float) -> float:
    return max(_ATTR_MIN, min(_ATTR_MAX, v))


def _generate_neighbors(p: Participant) -> list[Participant]:
    neighbors = []
    for key in p.attributes:
        for delta in (+_ATTR_DELTA, -_ATTR_DELTA):
            attrs = dict(p.attributes)
            attrs[key] = _clamp(attrs[key] + delta)
            neighbors.append(Participant(name=p.name, attributes=attrs))
    return neighbors


def _mark_winning_path(node: TreeNode) -> None:
    node.is_winning_path = True
    if not node.children:
        return
    for child in node.children:
        if child.value == node.value and not child.pruned:
            _mark_winning_path(child)
            return
    _mark_winning_path(node.children[0])


class MinimaxAlgorithm(Algorithm):
    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def evaluate(self, participant_a, participant_b, scorer) -> AlgorithmResult:
        root, value = self._minimax(participant_a, participant_b, self.depth, True, scorer)
        _mark_winning_path(root)
        sa, sb = scorer.score(participant_a), scorer.score(participant_b)
        if value >= 0:
            winner, loser, ws, ls = participant_a, participant_b, sa, sb
        else:
            winner, loser, ws, ls = participant_b, participant_a, sb, sa
        return AlgorithmResult(winner=winner, loser=loser, winner_score=ws, loser_score=ls, search_tree=root, search_path=None)

    def _minimax(self, pa, pb, depth, is_max, scorer):
        sa, sb = scorer.score(pa), scorer.score(pb)
        val = sa - sb
        label = f"{pa.name} vs {pb.name}"
        if depth == 0:
            return TreeNode(label=label, value=val), val
        node = TreeNode(label=label, value=0.0)
        if is_max:
            best = float("-inf")
            for n in _generate_neighbors(pa):
                child, cv = self._minimax(n, pb, depth - 1, False, scorer)
                node.children.append(child)
                if cv > best:
                    best = cv
        else:
            best = float("inf")
            for n in _generate_neighbors(pb):
                child, cv = self._minimax(pa, n, depth - 1, True, scorer)
                node.children.append(child)
                if cv < best:
                    best = cv
        node.value = best
        return node, best
