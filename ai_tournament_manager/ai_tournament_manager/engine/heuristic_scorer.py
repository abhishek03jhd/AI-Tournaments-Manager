from __future__ import annotations
from ai_tournament_manager.domain.models import Participant


class HeuristicScorer:
    def score(self, participant: Participant) -> float:
        attrs = participant.attributes
        if not attrs:
            participant.heuristic_score = 0.0
            return 0.0
        result = sum(attrs.values()) / len(attrs)
        participant.heuristic_score = result
        return result

    def tiebreak(self, a: Participant, b: Participant) -> Participant:
        if not a.attributes:
            return a
        first_key = next(iter(a.attributes))
        if b.attributes.get(first_key, 0.0) > a.attributes.get(first_key, 0.0):
            return b
        return a
