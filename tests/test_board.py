#!/usr/bin/env python

from copy import deepcopy
import os
import unittest

from src.board import Board
from src.board_error_flags import BoardErrorFlags
from src.game_state import GameState
from src.geometry import Geometry as G
from src.geometry import *
from src.hex_pos import HexPos
from src.hex_vec import HexVec
from src.move import Move
from src.pgn import Pgn
from src.piece_type import PieceType
from src.player import Player


class TestBoard(unittest.TestCase):
    def setUp(self):
        print(f'===== Running Board test: {self.id()} =====')

    def test_board_print(self):
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

    def test_fools_mate(self):
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

        move_texts = 'Qe1c3 Qe10c6 b1b2 b7b6 Bf3b1 e7e6 Qc3xBf9#'.split()
        for k, move_text in enumerate(move_texts):
            move = Pgn.move_text_to_move(b, move_text)
            b.move_make(move)
            self.assertEqual(b.halfmove_count, k + 1)
            self.assertEqual(b.get_fen_board(), FOOLS_FEN_BOARDS[k + 1])
            self.assertEqual(b.get_zobrist_hash(), FOOLS_ZOBRIST_HASHES[k + 1])
        # TODO: self.assertTrue(b.is_checkmate)


class TestBoardConstructor(unittest.TestCase):
    @unittest.skip
    def test_init_empty(self):
        pass

    def test_init_board_standard(self):
        # Default initialization
        b0 = Board()
        fen_board = '6/p5P/rp4PR/n1p3P1N/q2p2P2Q/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6'

        # Initialization from FEN (board) string
        b1 = Board(fen_board)
        zh0 = b0.get_zobrist_hash()
        zh1 = b1.get_zobrist_hash()
        self.assertEqual(b1.get_zobrist_hash(), b0.get_zobrist_hash())

        fen_board1 = b1.get_fen_board()
        self.assertEqual(fen_board1, fen_board)
        fen1 = b1.get_fen()
        self.assertEqual(fen1, fen_board + ' w - - 0 1')

        # Initialization from layout dict
        b2 = Board(b1.get_layout_dict())
        zh2 = b2.get_zobrist_hash()
        self.assertEqual(zh2, zh1)

    # Moves per piece in their initial location. (Same for each player.)
    #     K:2,Q:6,R:6(3+3),B:12(2+8+2),N:8(4+4),P:17(2*8+1).
    #     Total: 51
    def test_init_piece_move_counts(self):
        INIT_LAYOUT_MOVE_COUNTS = list(map(int, """
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
            expected_count = INIT_LAYOUT_MOVE_COUNTS[npos]
            self.assertEqual(actual_count, expected_count,
                f'At {G.npos_to_alg(npos)}: legal move count {actual_count} != {expected_count}')

    def test_init_piece_move_counts_total(self):
        b = Board()
        moves = b.get_moves_pseudolegal()
        self.assertEqual(len(moves), 51)

    @unittest.skip
    def test_piece_add(self):
        pass

    @unittest.skip
    def test_piece_remove(self):
        pass


class TestBoardDetectEndgame(unittest.TestCase):

    @unittest.skip
    def test_detect_check(self):
        pass

    def test_detect_checkmate(self):
        # Minimal layout
        layout_dict1 = {
                Player.Black: {
                    PieceType.King:  [G.F11],
                    },
                Player.White: {
                    PieceType.Queen:  [G.E8],
                    PieceType.Knight: [G.K6]
                    }
                }
        b1 = Board(layout_dict1)
        m1 = Move(G.alg_to_npos('k6'), G.alg_to_npos('g8'))
        m1.pt = PieceType.Knight
        b1.move_make(m1)
        # TODO: self.assertTrue(b1.is_checkmate)

        # Layout from the penultimate position of Fool's Mate
        layout_dict2 = {
                Player.Black: {
                    PieceType.King:   [G.G10],
                    PieceType.Queen:  [G.C6],
                    PieceType.Rook:   [G.C8, G.I8],
                    PieceType.Bishop: [G.F11, G.F10, G.F9],
                    PieceType.Knight: [G.D9, G.H9],
                    PieceType.Pawn:   [G.B6, G.C7, G.D7, G.E6,
                        G.F7,
                        G.G7, G.H7, G.I7, G.K7]
                },
                Player.White: {
                    PieceType.King:   [G.G1],
                    PieceType.Queen:  [G.C3],
                    PieceType.Rook:   [G.C1, G.I1],
                    PieceType.Bishop: [G.B1, G.F2, G.F1],
                    PieceType.Knight: [G.D1, G.H1],
                    PieceType.Pawn:   [G.B2, G.C2, G.D3, G.E4,
                        G.F5,
                        G.G4, G.H3, G.I2, G.K1]
                }
                }
        b2 = Board(layout_dict2)
        m2 = Move(G.alg_to_npos('c3'), G.alg_to_npos('f9'))
        m2.pt = PieceType.Queen
        b2.move_make(m2)
        # TODO: self.assertTrue(b2.is_checkmate)

    # Technically, insufficient material is a subset of dead game.
    @unittest.skip
    def test_detect_insufficient_material(self):
        pass

    def test_detect_nonprogress(self):
        MOVE_TEXTS_REPEATING = {
            Player.Black: ['Kg10g9', 'Kg9g10'],
            Player.White: ['Kg1g2', 'Kg2g1']
            }

        b = Board()

        # TODO: Use move diverse moves, such as inserting Pawn moves
        #   to reset non-progress counter, thereby avoiding the need
        #   to disable repetition checks.
        b.disable_check_repetition()

        move_nums = {}
        move_nums[Player.Black] = 0
        move_nums[Player.White] = 0

        def get_next_move(b: Board):
            player = b.cur_player
            move_ind = move_nums[player] % 2
            move_nums[player] += 1
            move_text = MOVE_TEXTS_REPEATING[player][move_ind]
            move_spec = Pgn.move_text_to_move_spec(move_text)
            moves = b.get_moves_matching(move_spec, move_text)
            self.assertEqual(len(moves), 1)
            move = moves[0]
            self.assertTrue(move.fr_npos)
            self.assertTrue(move.to_npos)
            self.assertTrue(b.pieces[move.fr_npos])
            return move

        for k in range(1, 100):
            next_move = get_next_move(b)
            b.move_make(next_move)
            self.assertFalse(b.is_50_move_rule_triggered)
            self.assertFalse(b.is_75_move_rule_triggered)

        # Make the 100th non-progress halfmove
        b.move_make(get_next_move(b))
        self.assertTrue(b.is_50_move_rule_triggered)
        self.assertFalse(b.is_75_move_rule_triggered)

        for k in range(100, 149):
            b.move_make(get_next_move(b))
            self.assertTrue(b.is_50_move_rule_triggered)
            self.assertFalse(b.is_75_move_rule_triggered)

        # Make the 150th non-progress halfmove
        # TODO: b.move_make(get_next_move(b))
        # TODO: self.assertTrue(b.is_50_move_rule_triggered)
        # TODO: self.assertTrue(b.is_75_move_rule_triggered)

    def test_detect_repetition(self):
        MOVE_TEXTS_REPEATING = {
            Player.Black: ['Kg10g9', 'Kg9g10'],
            Player.White: ['Kg1g2', 'Kg2g1']
            }

        b = Board()
        move_nums = {}
        move_nums[Player.Black] = 0
        move_nums[Player.White] = 0

        def get_next_move():
            player = b.cur_player
            move_ind = move_nums[player] % 2
            move_nums[player] += 1
            move_text = MOVE_TEXTS_REPEATING[player][move_ind]
            move_spec = Pgn.move_text_to_move_spec(move_text)
            moves = b.get_moves_matching(move_spec, move_text)
            self.assertEqual(len(moves), 1)
            return moves[0]

        for k in range(0, 6 + 1):
            m = get_next_move()
            # print(f'JMC: test_detect_repetition: next move={m}')
            b.move_make(m)
            self.assertFalse(b.is_repetition_3x)
            self.assertFalse(b.is_repetition_5x)

        # Create the 3rd duplicate
        b.move_make(get_next_move())
        self.assertTrue(b.is_repetition_3x)
        self.assertFalse(b.is_repetition_5x)

        for k in range(8, 14 + 1):
            b.move_make(get_next_move())
            self.assertTrue(b.is_repetition_3x)
            self.assertFalse(b.is_repetition_5x)

        # Create the 5th duplicate
        # TODO: b.move_make(get_next_move())
        # TODO: self.assertTrue(b.is_repetition_3x)
        # TODO: self.assertTrue(b.is_repetition_5x)

    def test_detect_stalemate(self):
        layout = {
            Player.Black: {
                PieceType.King: [G.F11],
                PieceType.Queen: [G.D2, G.H9]
                },
            Player.White: {
                PieceType.King: [G.G2]
                }
            }
        b = Board(layout)
        move_w = Pgn.move_text_to_move(b, 'Kg2h1')
        b.move_make(move_w)
        move_b = Pgn.move_text_to_move(b, 'Qh9h2')
        b.move_make(move_b)
        # TODO: self.assertEqual(b.game_state, GameState.WinStalemateBlack)


class TestBoardDetectError(unittest.TestCase):

    def test_detect_error_ep_target_location(self):
        b = Board()
        m = Pgn.move_text_to_move(b, 'b1b3')
        b.move_make(m)
        self.assertEqual(b.ep_target, G.alg_to_npos('b2'))

    def test_detect_error_excess_pieces(self):
        layout1 = deepcopy(G.INIT_LAYOUT_DICT)
        layout1[Player.Black][PieceType.Queen].append(G.E9)
        b1 = Board(layout1)
        errors1: BoardErrorFlags = b1.get_board_errors()
        self.assertTrue(errors1 & BoardErrorFlags.ExcessPieces)

        layout2 = deepcopy(G.INIT_LAYOUT_DICT)
        layout2[Player.White][PieceType.Queen].append(G.E2)
        b2 = Board(layout2)
        errors2: BoardErrorFlags = b2.get_board_errors()
        self.assertTrue(errors2 & BoardErrorFlags.ExcessPieces)

        layout3 = deepcopy(G.INIT_LAYOUT_DICT)
        layout3[Player.Black][PieceType.King].append(G.G9)

        b3 = Board(layout3)
        errors3: BoardErrorFlags = b3.get_board_errors()
        self.assertTrue(errors3 & BoardErrorFlags.ExcessKings)

    def test_detect_error_missing_king(self):
        layout1 = deepcopy(G.INIT_LAYOUT_DICT)
        layout1[Player.Black][PieceType.King] = []
        b1 = Board(layout1)
        errors1: BoardErrorFlags = b1.get_board_errors()
        self.assertTrue(errors1 & BoardErrorFlags.MissingKing)

    def test_detect_error_pawn_in_court(self):
        layout_dict = deepcopy(G.INIT_LAYOUT_DICT)
        layout_dict[Player.Black][PieceType.Pawn].append(G.F8)
        b = Board(layout_dict)
        errors: BoardErrorFlags = b.get_board_errors()
        self.assertTrue(errors & BoardErrorFlags.PawnInCourt)


class TestBoardMoves(unittest.TestCase):
    @unittest.skip
    def test_move_counts_by_piece_type(self):
        pass

    @unittest.skip
    def test_get_moves_legal(self):
        pass

    @unittest.skip
    def test_get_moves_pseudolegal(self):
        pass

    def test_undo_moves_initial(self):
        b = Board()
        zhash0 = b.get_zobrist_hash()
        initial_moves = b.get_moves_pseudolegal()
        self.assertEqual(len(initial_moves), 51)
        for k, move in enumerate(initial_moves):
            b.move_make(move)
            self.assertNotEqual(b.get_zobrist_hash(), zhash0)
            b.move_undo()
            self.assertEqual(b.get_zobrist_hash(), zhash0)


class TestBoardPuzzles(unittest.TestCase):
    def test_detect_mate_in_one(self):
        pass

    def test_detect_mate_in_two(self):
        pass


if __name__ == '__main__':
    unittest.main()
