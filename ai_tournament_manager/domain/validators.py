"""Input validation functions for the AI Tournament Manager."""

VALID_PARTICIPANT_COUNTS = {2, 4, 8, 16, 32, 64}
MAX_NAME_LENGTH = 50
ATTRIBUTE_MIN = 1.0
ATTRIBUTE_MAX = 100.0


class ValidationError(Exception):
    """Raised when user-supplied input fails domain validation."""


def validate_participant_count(n: int) -> None:
    """Raise ValidationError if n is not a valid tournament size.

    Valid sizes are powers of two in {2, 4, 8, 16, 32, 64}.
    """
    if n not in VALID_PARTICIPANT_COUNTS:
        raise ValidationError(
            f"Participant count must be one of {sorted(VALID_PARTICIPANT_COUNTS)}, got {n}."
        )


def validate_participant_name(name: str) -> None:
    """Raise ValidationError if name is empty or longer than 50 characters."""
    if not name:
        raise ValidationError("Participant name must not be empty.")
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(
            f"Participant name must be at most {MAX_NAME_LENGTH} characters, "
            f"got {len(name)}."
        )


def validate_attribute_value(value: float) -> None:
    """Raise ValidationError if value is outside the range [1, 100]."""
    if value < ATTRIBUTE_MIN or value > ATTRIBUTE_MAX:
        raise ValidationError(
            f"Attribute value must be between {ATTRIBUTE_MIN} and {ATTRIBUTE_MAX}, got {value}."
        )
