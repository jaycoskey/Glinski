#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import Enum


# The values of PieceType need to be positive integers, for
# collision-free computation of Move object hash functions.
class PieceType(Enum):
    King = 1
    Queen = 2
    Rook = 3
    Bishop = 4
    Knight = 5
    Pawn = 6

    def __str__(self):
        return self.to_symbol()

    def from_symbol(symbol):
        SYMBOL_TO_PT = {
            "K": King,
            "Q": Queen,
            "R": Rook,
            "B": Bishop,
            "N": Knight,
            "P": Pawn,
        }
        return SYMBOL_TO_PT[symbol]

    def to_symbol(self):
        PT_TO_SYMBOL = {
            "King": "K",
            "Queen": "Q",
            "Rook": "R",
            "Bishop": "B",
            "Knight": "N",
            "Pawn": "P",
        }
        return PT_TO_SYMBOL[self.name]
