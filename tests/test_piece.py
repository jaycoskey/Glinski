#!/usr/bin/env python
# by Jay M. Coskey, 2026

import unittest

from src.piece import Piece
from src.piece_type import PieceType
from src.player import Player


class TestPiece(unittest.TestCase):
    def test_piece_symbols(self):
        PTS = [PieceType.King, PieceType.Queen, PieceType.Rook,
               PieceType.Bishop, PieceType.Knight, PieceType.Pawn]
        PTS_STR_B = 'kqrbnp'
        PTS_STR_W = 'KQRBNP'

        pts_str_b = ''.join([str(Piece(Player.Black, pt)) for pt in PTS])
        self.assertEqual(pts_str_b, PTS_STR_B)

        pts_str_w = ''.join([str(Piece(Player.White, pt)) for pt in PTS])
        self.assertEqual(pts_str_w, PTS_STR_W)


if __name__ == '__main__':
    unittest.main()

