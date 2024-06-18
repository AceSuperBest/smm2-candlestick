from enum import Enum


class CommonGraphicsMode(Enum):
    grid = "grid"

class Direction(Enum):
    up = "up"
    down = "down"
    left = "left"
    right = "right"

class PasteMode(Enum):
    upper_left = "upper_left"
    vertical_center = "vertical_center"
    origin = "origin"


__all__ = ["CommonGraphicsMode", "Direction", "PasteMode"]