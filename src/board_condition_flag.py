#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import IntFlag


class BoardConditionFlag(IntFlag):
    IsCheck = 1
    IsMate = 2
    IsPostPawnHop = 4
    IsNonProgressMoves50 = 8
    IsNonProgressMoves75 = 16
    IsRepetition3 = 32
    IsRepetition5 = 64
