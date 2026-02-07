#!/usr/bin/env python

import unittest

from src.board import Board
from src.geometry import Geometry as G
from src.hex_pos import HexPos
from src.hex_vec import HexVec
from src.move import Move
from src.piece_type import PieceType


class TestBoard(unittest.TestCase):
    def test_board_contains_all_spaces(self):
        b = Board()
        for k in range(91):
            pos = HexPos(G.COORD_HEX0[k], G.COORD_HEX1[k])
            self.assertTrue(G.is_pos_on_board(pos))

    def test_detect_check(self):
        pass

    def test_detect_checkmate(self):
        pass

    # Technically, insufficient material is a subset of dead game.
    def test_detect_insufficient_material(self):
        pass

    def test_detect_mate_in_one(self):
        pass

    def test_detect_mate_in_two(self):
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

    @unittest.expectedFailure  # Board's compute_board_state has not yet been implemented
    def test_fools_mate(self):
        # 1. Move('Qe1c3')
        w1 = Move(G.alg_to_npos('e1'), G.alg_to_npos('c3'), None)

        # 1. ... Move('Qe10c6')
        b1 = Move(G.alg_to_npos('e10'), G.alg_to_npos('c6'), None)
        # --------------------
        # 2. Move('b1b2')
        w2 = Move(G.alg_to_npos('b1'), G.alg_to_npos('b2'), None)

        # ... Move('b7b6')
        b2 = Move(G.alg_to_npos('b7'), G.alg_to_npos('b6'), None)
        # --------------------
        # 3. Move('Bf3b1')
        w3 = Move(G.alg_to_npos('f3'), G.alg_to_npos('b1'), None)

        # ... Move('e7e6')
        b3 = Move(G.alg_to_npos('e7'), G.alg_to_npos('e6'), None)
        # --------------------
        moves = [w1, b1, w2, b2, w3, b3]

        b = Board()
        self.assertFalse(b.is_checkmate)
        for m in moves:
            b.move_make(m)
            self.assertFalse(b.is_checkmate)

        # 4. Move('Qc3xBf9#')
        w4 = Move(G.alg_to_npos('c3'), G.alg_to_npos('f9'), None)
        w4.capt_pt = PieceType.Bishop

        b.move_make(w4)
        b.print()
        self.assertTrue(b.is_checkmate)

    def test_get_moves_legal(self):
        pass

    def test_get_moves_pseudolegal(self):
        pass

    # Moves per piece in their initial location. (Same for each player.)
    #     K:2,Q:6,R:6(3+3),B:12(2+8+2),N:8(4+4),P:17(2*8+1).
    #     Total: 51
    def test_init_piece_move_counts(self):
        INIT_PIECE_MOVE_COUNTS = list(map(int, """
                  0   0   0   0   0   0
                2   0   0   0   0   0   2
              3   2   0   0   0   0   2   3
            4   0   2   0   0   0   2   0   4
          6   0   0   2   0   0   2   0   0   6
        2   8   2   0   1   0   1   0   2   8   2
          2   0   0   2   0   0   2   0   0   2
            4   0   2   0   0   0   2   0   4
              3   2   0   0   0   0   2   3
                2   0   0   0   0   0   2
                  0   0   0   0   0   0
                  """.split()))
        b = Board()
        for npos in range(G.SPACE_COUNT):
            piece = b.pieces[npos]
            if piece and piece.player != b.cur_player:
                continue
            actual_count = len(list(b.get_moves_pseudolegal_from(npos)))
            expected_count = INIT_PIECE_MOVE_COUNTS[npos]
            self.assertEqual(actual_count, expected_count,
                    f'At {G.npos_to_alg(npos)}: {actual_count} != {expected_count}')

    @unittest.skip("b.get_moves_pseudolegal() not yet implemented")
    def test_init_piece_move_counts_total(self):
        b = Board()
        moves = b.get_moves_pseudolegal()
        self.assertionEqual(len(moves), 51)

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

    def test_printout(self):
        expected = """
                  b
                q   k
              n   b   n
            r   -   -   r
          p   -   b   -   p
        -   p   -   -   p   -
          -   p   -   p   -
        -   -   p   p   -   -
          -   -   p   -   -
        -   -   -   -   -   -
          -   -   -   -   -
        -   -   -   -   -   -
          -   -   P   -   -
        -   -   P   P   -   -
          -   P   -   P   -
        -   P   -   -   P   -
          P   -   B   -   P
            R   -   -   R
              N   B   N
                Q   K
                  B
                  """

        b = Board()
        returned_lines = [row.strip() for row in b.get_print_str().split('\n')]
        expected_lines = [row.strip() for row in expected.split('\n') if len(row.strip()) > 0]
        self.assertEqual(len(returned_lines), len(expected_lines))

        for k in range(len(expected_lines)):
            self.assertEqual(returned_lines[k], expected_lines[k])


if __name__ == '__main__':
    unittest.main()
