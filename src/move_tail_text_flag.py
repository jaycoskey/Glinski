#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import IntEnum


class MoveTailTextFlag(IntFlag):
    Check = 1
    Mate = 2

    Promo_Q = 4
    Promo_R = 8
    Promo_D = 16
    Promo_N = 32
