#!/usr/bin/env python
# by Jay M. Coskey, 2026

from dataclasses import dataclass
from enum import Enum, auto

from src.hex_vec import HexVec

# Notes on converting between different position representations:
#   alg_to_pos  (geometry.py)
#   npos_to_alg (geometry.py)
#   npos_to_bb  (bitboard.py)
#   npos_to_pos (geometry.py)
#   pos_to_alg  (geometry.py)
#   pos_to_npos (geometry.py)
#
@dataclass(frozen=True)
class HexPos:
    hex0: int
    hex1: int

    def __add__(self, other: HexVec):
        return HexPos(self.hex0 + other.hex0, self.hex1 + other.hex1)

    def __eq__(self, other: "HexPos"):
        return self.hex0 == other.hex0 and self.hex1 == other.hex1

    def __iadd__(self, other: HexVec):
        self.hex0 += other.hex0
        self.hex1 += other.hex1

    def __ne__(self, other: "HexPos"):
        return not self.__eq__(other)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "({0}, {1})".format(self.hex0, self.hex1)

    def __sub__(self, other: "HexPos"):
        return HexVec(self.hex0 - other.hex0, self.hex1 - other.hex1)

    # GREP: Choice of coordinates
    # TODO: DESIGN: Consider moving this to geometry.py.
    def rank(self):
        return 6 - (self.hex0 if self.hex0 > 0 else 0) + self.hex1
