#!/usr/bin/env python

import unittest

from src.board import Board
from src.geometry import Geometry as G
from src.piece_type import PIECE_TYPE_COUNT
from src.player import PLAYER_COUNT

from src.zobrist import ZOBRIST_HASH_TABLE


class TestZobrist(unittest.TestCase):
    def test_zobrist_table_size(self):
        expected_size = G.SPACE_COUNT * PLAYER_COUNT * PIECE_TYPE_COUNT
        self.assertEqual(len(ZOBRIST_HASH_TABLE), expected_size)

    def test_zobrist_default_placement(self):
        b = Board()
        zhash = b.get_zobrist_hash()
        expected_hash = 0x9270EF137EC7189F
        self.assertEqual(zhash, expected_hash)

if __name__ == '__main__':
    unittest.main()
