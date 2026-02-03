#!/usr/bin/env python
# by Jay M. Coskey, 2026

from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class HexVec:
    hex0: int
    hex1: int

    def __add__(self, other: "HexVec"):
        return HexVec(self.hex0 + other.hex0, self.hex1 + other.hex1)

    def __eq__(self, other: "HexVec"):
        return self.hex0 == other.hex0 and self.hex1 == other.hex1

    def __mul__(self, n: int):
        return HexVec(n * self.hex0, n * self.hex1)

    def __ne__(self, other: "HexVec"):
        return HexVec(n * self.hex0, n * self.hex1)

    def __rmul__(self, n: int):
        return HexVec(n * self.hex0, n * self.hex1)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<{0}, {1}>".format(self.hex0, self.hex1)

    def __sub__(self, other: "HexVec"):
        return HexVec(self.hex0 - other.hex0, self.hex1 - other.hex1)

