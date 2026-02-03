#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import IntFlag


class MoveErrorFlag(IntFlag):
    InvalidCapture = 1
    InvalidEnPassant = 2
    InvalidMoveForBishop = 4
    InvalidMoveForKing = 8
    InvalidMoveForKnight = 16
    InvalidMoveForPawn = 32
    InvalidMoveForQueen = 64
    InvalidMoveForRook = 128
    InvalidPawnPromotion = 256
    PieceNotAtStartingSpace = 512

    def __str__(self):
        _MOVE_ERROR_TO_STR = {
            "NoError": "No error detected",
            "InvalidCapture": "Capture is not valid",
            "InvalidEnPassant": "En passant is not valid",
            "InvalidMoveForBishop": "Bishop move is not valid",
            "InvalidMoveForKing": "King move is not valid",
            "InvalidMoveForKnight": "Knight move is not valid",
            "InvalidMoveForPawn": "Pawn move is not valid",
            "InvalidMoveForQueen": "Queen move is not valid",
            "InvalidMoveForRook": "Rook move is not valid",
            "InvalidPawnPromotion": "Pawn promotion is not valid",
            "PieceNotAtStartingSpace": "Piece is not at starting space",
        }

        return _MOVE_ERROR_TO_STR[self.name]
