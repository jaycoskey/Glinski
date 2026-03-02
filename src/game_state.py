#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import auto, Enum


# Wins are further detailed in class GameDraw
class GameState(Enum):
    Unstarted = auto()
    InPlay = auto()

    Abandoned = auto()
    Draw = auto()
    WinBlack = auto()
    WinBlackStalemate = auto()
    WinWhite = auto()
    WinWhiteStalemate = auto()

