#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import Enum

PLAYER_COUNT = 2


class Player(Enum):
    Black = 0
    White = 1

    def __str__(self):
        if self == Player.Black:
            return "B"
        else:
            return "W"

    def opponent(self):
        cls = self.__class__
        vals = list(cls)
        opp_ind = (vals.index(self) + 1) % 2
        return vals[opp_ind]

PLAYERS = [Player.Black, Player.White]

