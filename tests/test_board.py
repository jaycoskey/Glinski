#!/usr/bin/env python

import unittest

from src.board import Board
from src.geometry import Geometry as G
from src.hex_pos import HexPos
from src.hex_vec import HexVec
from src.piece_type import PieceType


class Test_Board(unittest.TestCase):
    def test_board_contains_all_spaces(self):
        pass

    def test_detect_check(self):
        pass

    def test_detect_checkmate(self):
        pass

    def test_detect_insufficient_material(self):  # Technically, a subset of a dead game
        pass

    def test_detect_mate_in_one(self):
        pass

    def test_detect_mate_in_two(self):
        pass

    def test_detect_mate_in_three(self):
        pass

    def test_detect_stalemate(self):
        pass

    def test_detect_error_ep_target_location(self):
        pass

    def test_detect_error_excess_pieces(self):
        pass

    def test_detect_error_missing_king(self):
        pass

    def test_detect_error_pawn_in_court(self):
        pass

    def test_detect_nonprogress_moves_50(self):
        pass

    def test_detect_nonprogress_moves_75(self):
        pass

    def test_detect_repetition3x(self):
        pass

    def test_detect_repetition5x(self):
        pass

    def test_get_moves_legal(self):
        pass

    def test_get_moves_pseudolegal(self):
        pass

    def test_init_piece_move_counts(self):
        pass

    def test_init_piece_move_counts_total(self):
        pass

    def test_init_by_fen(self):
        pass

    def test_init_by_placement_data(self):
        pass

    def test_init_empty(self):
        pass

    def test_move_counts_by_piece_type(self):
        pass

    def test_pieces_add(self):
        pass

    def test_pieces_remove(self):
        pass

    def test_zobrist_hash(self):
        pass


if __name__ == '__main__':
    unittest.main()
