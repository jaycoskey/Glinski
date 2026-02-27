#!/usr/bin/env python
# by Jay M. Coskey, 2026

from src.piece_type import PieceType
from src.player import Player


class Piece:
    player: Player
    pt: PieceType

    def __init__(self, player: Player, pt: PieceType):
        self.player = player
        self.pt = pt

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        result = str(self.pt)
        if self.player == Player.Black:
            result = result.lower()
        return result

    @classmethod
    def fen_symbol_to_player_pt(cls, c: str) -> (Player, PieceType):
        player = Player.Black if c.islower() else Player.White
        pt = PieceType.from_symbol(c.upper())
        return (player, pt)

