#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import IntFlag


class BoardErrorFlag(IntFlag):
    ExcessKings = 1
    ExcessPawns = 2
    ExcessPieces = 4
    InvalidEpTarget = 8
    MissingKing = 16
    PawnInCourt = 32
    PawnOnBackRank = 64
