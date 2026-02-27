#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import auto, Enum


class BoardState(Enum):
    Normal = auto()
    Check = auto()
    Checkmate = auto()
    Draw = auto()
    Stalemate = auto()

