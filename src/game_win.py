#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import auto, Enum


class GameWin(Enum):
    Agreement = auto()
    Checkmate = auto()
    Stalemate = auto()
    # Time = auto()
