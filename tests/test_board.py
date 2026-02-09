#!/usr/bin/env python

import unittest

from src.board import Board
from src.geometry import Geometry as G
from src.geometry import *
from src.hex_pos import HexPos
from src.hex_vec import HexVec
from src.move import Move
from src.piece_type import PieceType
from src.player import Player


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

    def test_fools_mate(self):
        # 1. Move('Qe1c3')
        w1 = Move(G.alg_to_npos('e1'), G.alg_to_npos('c3'), None)
        w1.pt = PieceType.Queen
        # 1. ... Move('Qe10c6')
        b1 = Move(G.alg_to_npos('e10'), G.alg_to_npos('c6'), None)
        b1.pt = PieceType.Queen

        # --------------------
        # 2. Move('b1b2')
        w2 = Move(G.alg_to_npos('b1'), G.alg_to_npos('b2'), None)
        w2.pt = PieceType.Pawn

        # ... Move('b7b6')
        b2 = Move(G.alg_to_npos('b7'), G.alg_to_npos('b6'), None)
        b2.pt = PieceType.Pawn

        # --------------------
        # 3. Move('Bf3b1')
        w3 = Move(G.alg_to_npos('f3'), G.alg_to_npos('b1'), None)
        w3.pt = PieceType.Bishop

        # ... Move('e7e6')
        b3 = Move(G.alg_to_npos('e7'), G.alg_to_npos('e6'), None)
        b3.pt = PieceType.Pawn

        # --------------------
        moves = [w1, b1, w2, b2, w3, b3]

        FOOLS_FEN_BOARDS = [
                "6/p5P/rp4PR/n1p3P1N/q2p2P2Q/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/p5P/rp3QPR/n1p3P1N/q2p2P3/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/p5P/rpq2QPR/n1p3P1N/3p2P3/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/p4P1/rpq2QPR/n1p3P1N/3p2P3/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/1p3P1/rpq2QPR/n1p3P1N/3p2P3/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/1p3PB/rpq2QPR/n1p3P1N/3p2P3/bbb1p1P2BB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/1p3PB/rpq2QPR/n1p3P1N/4p1P3/bbb1p1P2BB/k2p2P2K/n1p3P1N/rp4PR/p5P/6",
                "6/1p3PB/rpq3PR/n1p3P1N/4p1P3/bbQ1p1P2BB/k2p2P2K/n1p3P1N/rp4PR/p5P/6"
                ]

        FOOLS_ZOBRIST_HASHES = [
                0x9270ef137ec7189f,
                0xef0c315ccbbc8829,
                0x31c93c2c36c66211,
                0x39102ab2cf975366,
                0xe7ef9ec63c14c8d8,
                0x0712bf1f064d3996,
                0x4dbc13af9b83a6df,
                0xb194f93e12661e90,
                ]

        b = Board()
        self.assertEqual(b.get_fen_board(), FOOLS_FEN_BOARDS[0])
        self.assertEqual(b.get_zobrist_hash(), FOOLS_ZOBRIST_HASHES[0])
        self.assertFalse(b.is_checkmate)
        for k, move in enumerate(moves):
            b.move_make(move)
            self.assertEqual(b.halfmove_count, k + 1)
            self.assertEqual(b.get_fen_board(), FOOLS_FEN_BOARDS[k + 1])
            self.assertEqual(b.get_zobrist_hash(), FOOLS_ZOBRIST_HASHES[k + 1])
            self.assertEqual(len(b.history_zobrist_hash), b.halfmove_count + 1)
            self.assertEqual(b.get_max_repetition_count(), 1)
            self.assertFalse(b.is_checkmate)

        # 4. Move('Qc3xBf9#')
        w4 = Move(G.alg_to_npos('c3'), G.alg_to_npos('f9'), None)
        w4.pt = PieceType.Queen
        # TODO: Include the following few lines, once Checkmate detection is complete.
        # b.move_make(w4)  # This move causes checkmate.

        # self.assertEqual(b.get_fen_board(), FOOLS_FEN_BOARDS[-1])
        # self.assertEqual(b.get_zobrist_hash(), FOOLS_ZOBRIST_HASHES[-1])
        # self.assertTrue(b.is_checkmate)

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

    def test_init_empty(self):
        pass

    def test_init_placement_data(self):
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

    def test_undo_moves_initial(self):
        b = Board()
        zhash0 = b.get_zobrist_hash()
        for k, move in enumerate(b.get_moves_pseudolegal()):
            b.move_make(move)
            self.assertNotEqual(b.get_zobrist_hash(), zhash0)
            b.move_undo()
            self.assertEqual(b.get_zobrist_hash(), zhash0)

    def test_get_moves_legal(self):
        pass


if __name__ == '__main__':
    unittest.main()
