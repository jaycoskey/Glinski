#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import auto, Enum


class GameState(Enum):
    Abandoned = auto()
    InPlay = auto()
    Unstarted = auto()

    Draw = auto()  # Further detailed in class GameDraw
    Stalemate_Win_Black = auto()
    Stalemate_Win_White = auto()
    Win_Black = auto()  # Further detailed in class GameWin
    Win_White = auto()  # Further detailed in class GameWin
