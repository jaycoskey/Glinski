#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import auto, Enum


class MoveEval(Enum):
    MoveEval_None = auto()

    Good = auto()
    Brilliant = auto()
    Bad = auto()
    Blunder = auto()
    Interesting = auto()
    Dubious = auto()

    def to_str(self):
        __STR__ = {
            "MoveEval_None": "",
            "Good": "!",
            "Brilliant": "!!",
            "Bad": "?",
            "Blunder": "??",
            "Interesting": "!?",
            "Dubious": "?!",
        }

        return __STR__[self.name]
