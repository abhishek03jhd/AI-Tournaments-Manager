from enum import Enum


class AlgorithmType(Enum):
    MINIMAX = "Minimax"
    ALPHA_BETA = "Alpha-Beta Pruning"
    HILL_CLIMBING = "Hill Climbing"


class SeedingMode(Enum):
    RANDOM = "random"
    USER_DEFINED = "user_defined"
