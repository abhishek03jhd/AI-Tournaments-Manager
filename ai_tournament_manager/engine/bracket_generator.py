"""Bracket generation for single-elimination tournaments."""

import math
import random

from ai_tournament_manager.domain.enums import SeedingMode
from ai_tournament_manager.domain.models import Bracket, Match, Participant, Round
from ai_tournament_manager.domain.validators import validate_participant_count


def _round_label(round_number: int, total_rounds: int) -> str:
    """Return the human-readable label for a round.

    The label is determined by how many participants remain at the start of
    that round (i.e. 2 ** (total_rounds - round_number + 1)).
    """
    participants_in_round = 2 ** (total_rounds - round_number + 1)
    if participants_in_round == 2:
        return "Final"
    if participants_in_round == 4:
        return "Semi-Final"
    if participants_in_round == 8:
        return "Quarter-Final"
    return f"Round of {participants_in_round}"


class BracketGenerator:
    """Generates a full single-elimination bracket from a list of participants."""

    def generate(self, participants: list[Participant], seeding: SeedingMode) -> Bracket:
        """Build and return a Bracket for the given participants.

        Args:
            participants: The list of participants to seed into the bracket.
            seeding: RANDOM shuffles participants; USER_DEFINED preserves order.

        Returns:
            A fully-constructed Bracket with all rounds and matches populated.
            Matches in rounds after the first have participant_a/participant_b
            set to None (they are filled in as the tournament progresses).

        Raises:
            ValidationError: If the participant count is not in {2,4,8,16,32,64}.
        """
        validate_participant_count(len(participants))

        # Apply seeding
        if seeding == SeedingMode.RANDOM:
            seeded = list(participants)
            random.shuffle(seeded)
        else:
            seeded = list(participants)

        n = len(seeded)
        total_rounds = int(math.log2(n))

        rounds: list[Round] = []

        for round_num in range(1, total_rounds + 1):
            label = _round_label(round_num, total_rounds)
            matches_in_round = n // (2 ** round_num)
            matches: list[Match] = []

            for match_idx in range(1, matches_in_round + 1):
                match_id = f"R{round_num}M{match_idx}"

                if round_num == 1:
                    # Pair up seeded participants: slots (2i-2) and (2i-1)
                    slot_a = (match_idx - 1) * 2
                    slot_b = slot_a + 1
                    participant_a: Participant | None = seeded[slot_a]
                    participant_b: Participant | None = seeded[slot_b]
                else:
                    # Winners from the previous round fill these slots later
                    participant_a = None
                    participant_b = None

                matches.append(
                    Match(
                        id=match_id,
                        round_number=round_num,
                        participant_a=participant_a,
                        participant_b=participant_b,
                    )
                )

            rounds.append(Round(number=round_num, label=label, matches=matches))

        return Bracket(rounds=rounds)
