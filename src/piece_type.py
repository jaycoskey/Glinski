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

    @classmethod
    def from_symbol(cls, symbol, lang='en'):
        if lang == 'en':
            SYMBOL_TO_PT = {
                "K": PieceType.King,
                "Q": PieceType.Queen,
                "R": PieceType.Rook,
                "B": PieceType.Bishop,
                "N": PieceType.Knight,
                "P": PieceType.Pawn,
            }
        elif lang == 'hu':
            SYMBOL_TO_PT = {
                "K": PieceType.King,
                "V": PieceType.Queen,
                "B": PieceType.Rook,
                "F": PieceType.Bishop,
                "H": PieceType.Knight,
                "G": PieceType.Pawn,
            }
        else:
            raise NotImplementedError(f'Piece Type characters not supported for language {lang}')

        return SYMBOL_TO_PT[symbol]

    def to_symbol(self, lang='en'):
        if lang == 'en':
            PT_TO_SYMBOL = {
                "King": "K",
                "Queen": "Q",
                "Rook": "R",
                "Bishop": "B",
                "Knight": "N",
                "Pawn": "P"
                }
        elif lang == 'hu':
            PT_TO_SYMBOL = {
                "King": "K",
                "Queen": "V",
                "Rook": "B",
                "Bishop": "F",
                "Knight": "H",
                "Pawn": "G"
                }
        else:
            raise NotImplementedError(f'Piece Type characters not supported for language {lang}')

        return PT_TO_SYMBOL[self.name]

    def to_unicode(self, player):
        unicode_symbols = [
                {
                    'King':   '\u2654',
                    'Queen':  '\u2655',
                    'Rook':   '\u2656',
                    'Bishop': '\u2657',
                    'Knight': '\u2658',
                    'Pawn':   '\u2659'
                },
                {
                    'King':   '\u265A',
                    'Queen':  '\u265B',
                    'Rook':   '\u265C',
                    'Bishop': '\u265D',
                    'Knight': '\u265E',
                    'Pawn':   '\u265F'
                }]
        return unicode_symbols[player][self.name]

