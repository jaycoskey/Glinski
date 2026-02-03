#!/usr/bin/env python
# by Jay M. Coskey, 2026

from dataclasses import dataclass
from enum import Enum, auto

from src.hex_vec import HexVec


@dataclass(frozen=True)
class HexPos:
    hex0: int
    hex1: int

    def __add__(self, other: HexVec):
        return HexPos(self.hex0 + other.hex0, self.hex1 + other.hex1)

    def __eq__(self, other):
        return self.hex0 == other.hex0 and self.hex1 == other.hex1

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "({0}, {1})".format(self.hex0, self.hex1)

    def __sub__(self, other: "HexPos"):
        return HexVec(self.hex0 - other.hex0, self.hex1 - other.hex1)

    # GREP: Coordinate choice
    # TODO: DESIGN: Consider moving this to geometry.py.
    def rank(self):
        return 6 - (self.hex0 if self.hex0 > 0 else 0) + self.hex1
