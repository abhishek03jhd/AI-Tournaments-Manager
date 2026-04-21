import math
import random
from ai_tournament_manager.domain.enums import SeedingMode
from ai_tournament_manager.domain.models import Bracket, Match, Participant, Round
from ai_tournament_manager.domain.validators import validate_participant_count


def _round_label(round_number: int, total_rounds: int) -> str:
    participants_in_round = 2 ** (total_rounds - round_number + 1)
    if participants_in_round == 2:
        return "Final"
    if participants_in_round == 4:
        return "Semi-Final"
    if participants_in_round == 8:
        return "Quarter-Final"
    return f"Round of {participants_in_round}"


class BracketGenerator:
    def generate(self, participants: list[Participant], seeding: SeedingMode) -> Bracket:
        validate_participant_count(len(participants))
        seeded = list(participants)
        if seeding == SeedingMode.RANDOM:
            random.shuffle(seeded)
        n = len(seeded)
        total_rounds = int(math.log2(n))
        rounds: list[Round] = []
        for round_num in range(1, total_rounds + 1):
            label = _round_label(round_num, total_rounds)
            matches_in_round = n // (2 ** round_num)
            matches: list[Match] = []
            for match_idx in range(1, matches_in_round + 1):
                if round_num == 1:
                    slot_a = (match_idx - 1) * 2
                    pa, pb = seeded[slot_a], seeded[slot_a + 1]
                else:
                    pa, pb = None, None
                matches.append(Match(id=f"R{round_num}M{match_idx}", round_number=round_num,
                                     participant_a=pa, participant_b=pb))
            rounds.append(Round(number=round_num, label=label, matches=matches))
        return Bracket(rounds=rounds)
