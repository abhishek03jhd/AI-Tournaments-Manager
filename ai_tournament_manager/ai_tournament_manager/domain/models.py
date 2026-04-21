from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Participant:
    name: str
    attributes: dict[str, float]
    heuristic_score: float = 0.0


@dataclass
class AlgorithmResult:
    winner: Participant
    loser: Participant
    winner_score: float
    loser_score: float
    search_tree: TreeNode | None = None
    search_path: list[SearchState] | None = None


@dataclass
class TreeNode:
    label: str
    value: float
    alpha: float | None = None
    beta: float | None = None
    pruned: bool = False
    children: list[TreeNode] = field(default_factory=list)
    is_winning_path: bool = False


@dataclass
class SearchState:
    participant: Participant
    heuristic_value: float
    is_local_max: bool = False


@dataclass
class Match:
    id: str
    round_number: int
    participant_a: Participant | None
    participant_b: Participant | None
    winner: Participant | None = None
    algorithm_result: AlgorithmResult | None = None


@dataclass
class Round:
    number: int
    label: str
    matches: list[Match]


@dataclass
class Bracket:
    rounds: list[Round]
    champion: Participant | None = None

    def total_rounds(self) -> int:
        return len(self.rounds)

    def pending_matches(self) -> list[Match]:
        result = []
        for round_ in self.rounds:
            for match in round_.matches:
                if match.winner is None and match.participant_a is not None and match.participant_b is not None:
                    result.append(match)
        return result

    def is_complete(self) -> bool:
        for round_ in self.rounds:
            for match in round_.matches:
                if match.participant_a is not None and match.participant_b is not None:
                    if match.winner is None:
                        return False
        return True


@dataclass
class MatchResult:
    match: Match
    algorithm_result: AlgorithmResult
