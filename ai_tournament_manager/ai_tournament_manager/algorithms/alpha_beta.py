from __future__ import annotations
from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.algorithms.minimax import _generate_neighbors, _mark_winning_path
from ai_tournament_manager.domain.models import AlgorithmResult, Participant, TreeNode
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer


class AlphaBetaAlgorithm(Algorithm):
    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def evaluate(self, participant_a, participant_b, scorer) -> AlgorithmResult:
        root, value = self._ab(participant_a, participant_b, self.depth, True, float("-inf"), float("inf"), scorer)
        _mark_winning_path(root)
        sa, sb = scorer.score(participant_a), scorer.score(participant_b)
        if value >= 0:
            winner, loser, ws, ls = participant_a, participant_b, sa, sb
        else:
            winner, loser, ws, ls = participant_b, participant_a, sb, sa
        return AlgorithmResult(winner=winner, loser=loser, winner_score=ws, loser_score=ls, search_tree=root, search_path=None)

    def _ab(self, pa, pb, depth, is_max, alpha, beta, scorer):
        sa, sb = scorer.score(pa), scorer.score(pb)
        val = sa - sb
        label = f"{pa.name} vs {pb.name}"
        if depth == 0:
            return TreeNode(label=label, value=val, alpha=alpha, beta=beta), val
        node = TreeNode(label=label, value=0.0, alpha=alpha, beta=beta)
        pruned = False
        if is_max:
            best = float("-inf")
            for n in _generate_neighbors(pa):
                if pruned:
                    node.children.append(TreeNode(label=f"{n.name} vs {pb.name}", value=0.0, pruned=True))
                    continue
                child, cv = self._ab(n, pb, depth - 1, False, alpha, beta, scorer)
                node.children.append(child)
                if cv > best:
                    best = cv
                if best > alpha:
                    alpha = best
                    node.alpha = alpha
                if alpha >= beta:
                    pruned = True
            node.value = best
            return node, best
        else:
            best = float("inf")
            for n in _generate_neighbors(pb):
                if pruned:
                    node.children.append(TreeNode(label=f"{pa.name} vs {n.name}", value=0.0, pruned=True))
                    continue
                child, cv = self._ab(pa, n, depth - 1, True, alpha, beta, scorer)
                node.children.append(child)
                if cv < best:
                    best = cv
                if best < beta:
                    beta = best
                    node.beta = beta
                if beta <= alpha:
                    pruned = True
            node.value = best
            return node, best
