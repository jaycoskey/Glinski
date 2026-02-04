#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import Enum


PIECE_TYPE_COUNT = 6

class PieceType(Enum):
    King   = 0
    Queen  = 1
    Rook   = 2
    Bishop = 3
    Knight = 4
    Pawn   = 5

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
