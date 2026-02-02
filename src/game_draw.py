#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import auto, Enum


class GameDraw(Enum):
    GameDraw_None = auto()

    Agreement = auto()
    Claim_MoveRule_50 = auto()
    Claim_Repetition_3x = auto()
    DeadPosition = auto()
    InsufficientMaterial = auto()  # Technically, a subset of DeadPosition
    MoveRule_75 = auto()
    Repetition_5x = auto()
