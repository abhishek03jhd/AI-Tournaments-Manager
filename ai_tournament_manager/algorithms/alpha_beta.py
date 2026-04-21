from __future__ import annotations

from ai_tournament_manager.algorithms.base import Algorithm
from ai_tournament_manager.algorithms.minimax import _generate_neighbors, _mark_winning_path
from ai_tournament_manager.domain.models import AlgorithmResult, Participant, TreeNode
from ai_tournament_manager.engine.heuristic_scorer import HeuristicScorer


class AlphaBetaAlgorithm(Algorithm):
    """Alpha-Beta Pruning — same result as Minimax with fewer node evaluations."""

    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def evaluate(
        self,
        participant_a: Participant,
        participant_b: Participant,
        scorer: HeuristicScorer,
    ) -> AlgorithmResult:
        root, value = self._alpha_beta(
            participant_a, participant_b, self.depth,
            is_maximizing=True, alpha=float("-inf"), beta=float("inf"), scorer=scorer,
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
            winner=winner, loser=loser,
            winner_score=winner_score, loser_score=loser_score,
            search_tree=root, search_path=None,
        )

    def _alpha_beta(
        self,
        participant_a: Participant,
        participant_b: Participant,
        depth: int,
        is_maximizing: bool,
        alpha: float,
        beta: float,
        scorer: HeuristicScorer,
    ) -> tuple[TreeNode, float]:
        score_a = scorer.score(participant_a)
        score_b = scorer.score(participant_b)
        node_value = score_a - score_b
        label = f"{participant_a.name} vs {participant_b.name}"

        if depth == 0:
            return TreeNode(label=label, value=node_value, alpha=alpha, beta=beta), node_value

        node = TreeNode(label=label, value=0.0, alpha=alpha, beta=beta)

        if is_maximizing:
            neighbors = _generate_neighbors(participant_a)
            best_value = float("-inf")
            pruned = False
            for neighbor in neighbors:
                if pruned:
                    node.children.append(TreeNode(label=f"{neighbor.name} vs {participant_b.name}", value=0.0, pruned=True))
                    continue
                child, child_value = self._alpha_beta(neighbor, participant_b, depth - 1, False, alpha, beta, scorer)
                node.children.append(child)
                if child_value > best_value:
                    best_value = child_value
                if best_value > alpha:
                    alpha = best_value
                    node.alpha = alpha
                if alpha >= beta:
                    pruned = True
            node.value = best_value
            return node, best_value
        else:
            neighbors = _generate_neighbors(participant_b)
            best_value = float("inf")
            pruned = False
            for neighbor in neighbors:
                if pruned:
                    node.children.append(TreeNode(label=f"{participant_a.name} vs {neighbor.name}", value=0.0, pruned=True))
                    continue
                child, child_value = self._alpha_beta(participant_a, neighbor, depth - 1, True, alpha, beta, scorer)
                node.children.append(child)
                if child_value < best_value:
                    best_value = child_value
                if best_value < beta:
                    beta = best_value
                    node.beta = beta
                if beta <= alpha:
                    pruned = True
            node.value = best_value
            return node, best_value
