from enum import Enum


class CandleErrorStatus(Enum):
    NORMAL = 0
    SCORE_NEGATIVE = 1
    HIGH_LESS_THAN_MAX = 2
    LOW_GREATER_THAN_MIN = 3