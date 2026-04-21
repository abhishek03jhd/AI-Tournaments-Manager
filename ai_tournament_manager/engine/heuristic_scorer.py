from __future__ import annotations

from ai_tournament_manager.domain.models import Participant


class HeuristicScorer:
    """Deterministic heuristic scorer for tournament participants."""

    def score(self, participant: Participant) -> float:
        """Compute and store the heuristic score as a simple average of all numeric attributes.

        The result is deterministic: same attributes always produce the same score.
        Updates participant.heuristic_score in place and returns the value.
        """
        attrs = participant.attributes
        if not attrs:
            participant.heuristic_score = 0.0
            return 0.0
        total = sum(attrs.values())
        result = total / len(attrs)
        participant.heuristic_score = result
        return result

    def tiebreak(self, a: Participant, b: Participant) -> Participant:
        """Return the participant with the higher value in the first attribute key.

        If still equal, return participant_a.
        """
        if not a.attributes:
            return a
        first_key = next(iter(a.attributes))
        val_a = a.attributes.get(first_key, 0.0)
        val_b = b.attributes.get(first_key, 0.0)
        if val_b > val_a:
            return b
        return a
