#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import Enum


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


if __name__ == "__main__":
    b1 = Player.Black
    w1 = Player.White
    print(f"Black = {b1}")
    print(f"White = {w1}")

    print(f"Opponent of Black = {b1.opponent()}")
    print(f"Opponent of White = {w1.opponent()}")

    b2 = Player.Black
    w2 = Player.White
    assert b1 == b2
    assert w1 == w2

    assert b1 != w1
    assert b2 != w2
