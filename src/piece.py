#!/usr/bin/env python
# by Jay M. Coskey, 2026

from dataclasses import dataclass

from src.piece_type import PieceType
from src.player import Player


@dataclass(frozen=True)
class Piece:
    player: Player
    pt: PieceType

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        result = str(self.pt)
        if self.player == Player.Black:
            result = result.lower()
        return result
