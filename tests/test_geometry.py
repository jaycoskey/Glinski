#!/usr/bin/env python
# by Jay M. Coskey, 2026
# pylint: disable=invalid-name, too-many-locals

import unittest

from src.bitboard import BitBoard, BITBOARD_SPACES
from src.bitboard import BB_A1, BB_A6
from src.bitboard import BB_B2, BB_B4, BB_B6
from src.bitboard import BB_C3, BB_C4, BB_C5, BB_C6
from src.bitboard import BB_D2, BB_D3, BB_D4, BB_D5, BB_D6, BB_D7, BB_D8
from src.bitboard import BB_E3, BB_E4, BB_E5, BB_E6, BB_E7, BB_E8
from src.bitboard import BB_F1, BB_F2, BB_F3, BB_F4, BB_F5, BB_F6
from src.bitboard import BB_F7, BB_F8, BB_F9, BB_F10, BB_F11
from src.bitboard import BB_G3, BB_G4, BB_G5, BB_G6, BB_G7, BB_G8
from src.bitboard import BB_H2, BB_H3, BB_H4, BB_H5, BB_H6, BB_H7, BB_H8
from src.bitboard import BB_I3, BB_I4, BB_I5, BB_I6
from src.bitboard import BB_K2, BB_K4, BB_K6
from src.bitboard import BB_L1, BB_L6
from src.board_color import BoardColor
from src.geometry import Geometry as G
from src.hex_pos import HexPos
from src.hex_vec import HexVec


class TestGeometry(unittest.TestCase):
    def test_add_vecs12(self):
        self.assertEqual(sum(G.VECS_12, G.ZERO), G.ZERO)

    def test_add_knights_vecs(self):
        center = HexPos(5, 5)
        pos = center
        for k, kvec in enumerate(G.VECS_KNIGHT):
            pos = pos + kvec
            if k < 11:
                self.assertNotEqual(pos, center)
        self.assertEqual(pos, center)  # Back to where we started

    def test_add_pawn_capture_vecs(self):
        vec_bp = sum(G.VECS_PAWN_CAPT_BLACK, start=HexVec(0, 0))
        self.assertEqual(vec_bp, G.VECS_PAWN_ADV_BLACK)

        vec_wp = sum(G.VECS_PAWN_CAPT_WHITE, start=HexVec(0, 0))
        self.assertEqual(vec_wp, G.VECS_PAWN_ADV_WHITE)

    def test_board_color(self):
        def str_to_board_color(alg: str) -> BoardColor:
            npos = G.alg_to_npos(alg)
            return G.get_board_color(npos)

        self.assertTrue(str_to_board_color("f6"), BoardColor.Medium)

        self.assertTrue(str_to_board_color("a6"), BoardColor.Light)
        self.assertTrue(str_to_board_color("a1"), BoardColor.Dark)
        self.assertTrue(str_to_board_color("f6"), BoardColor.Dark)
        self.assertTrue(str_to_board_color("f1"), BoardColor.Light)
        self.assertTrue(str_to_board_color("l6"), BoardColor.Light)
        self.assertTrue(str_to_board_color("l1"), BoardColor.Dark)

    def test_constants(self):
        self.assertEqual(G.SPACE_COUNT, 91)

        self.assertEqual(G.A6, G.alg_to_pos("a6"))
        self.assertEqual(G.A1, G.alg_to_pos("a1"))
        self.assertEqual(G.F11, G.alg_to_pos("f11"))
        self.assertEqual(G.F1, G.alg_to_pos("f1"))
        self.assertEqual(G.L6, G.alg_to_pos("l6"))
        self.assertEqual(G.L1, G.alg_to_pos("l1"))

        self.assertEqual(G.npos_to_alg(0), "a6")
        self.assertEqual(G.npos_to_alg(5), "a1")
        self.assertEqual(G.npos_to_alg(40), "f11")
        self.assertEqual(G.npos_to_alg(45), "f6")
        self.assertEqual(G.npos_to_alg(50), "f1")
        self.assertEqual(G.npos_to_alg(85), "l6")
        self.assertEqual(G.npos_to_alg(90), "l1")

    def test_board_contains_all_spaces(self):
        for k in range(G.SPACE_COUNT):
            pos = HexPos(G.COORD_HEX0[k], G.COORD_HEX1[k])
            self.assertTrue(G.is_pos_on_board(pos))

    def test_conversion_pos_to_alg(self):
        NW = HexPos(-5, 0)
        SW = HexPos(-5, -5)
        self.assertEqual(G.pos_to_alg(NW), 'a6')
        self.assertEqual(G.pos_to_alg(SW), 'a1')

        N = HexPos( 0, 5)
        S = HexPos(0, -5)
        self.assertEqual(G.pos_to_alg(N), 'f11')
        self.assertEqual(G.pos_to_alg(S), 'f1')

        NE = HexPos(5, 5)
        SE = HexPos(5, 0)
        self.assertEqual(G.pos_to_alg(NE), 'l6')
        self.assertEqual(G.pos_to_alg(SE), 'l1')

    def test_leaps_king(self):
        computed = BitBoard(G.SPACE_COUNT)
        pos = G.F6
        npos = G.pos_to_npos(pos)
        for dest_npos in G.LEAPS_KING[npos]:
            computed |= BITBOARD_SPACES[dest_npos]
        expected = (BB_F7 | BB_G7 | BB_G6 | BB_H5 | BB_G5 | BB_G4
                | BB_F5 | BB_E4 | BB_E5 | BB_D5 | BB_E6 | BB_E7)
        self.assertEqual(computed, expected)

    def test_leaps_knight(self):
        computed = BitBoard(G.SPACE_COUNT)
        pos = G.F6
        npos = G.pos_to_npos(pos)
        for dest_npos in G.LEAPS_KNIGHT[npos]:
            computed |= BITBOARD_SPACES[dest_npos]

        expected = (BB_E8 | BB_G8
                | BB_H7 | BB_I5
                | BB_I4 | BB_H3
                | BB_G3 | BB_E3
                | BB_D3 | BB_C4
                | BB_C5 | BB_D7)
        self.assertEqual(computed, expected)

    def test_leaps_pawn(self):
        pos_b = G.F7
        npos_b = G.pos_to_npos(pos_b)
        pos_w = G.F5
        npos_w = G.pos_to_npos(pos_w)

        # --------------------

        computed_adv_b = BITBOARD_SPACES[G.LEAP_PAWN_ADV_BLACK[npos_b]]
        expected_adv_b = BB_F6
        self.assertEqual(computed_adv_b, expected_adv_b)

        computed_adv_w = BITBOARD_SPACES[G.LEAP_PAWN_ADV_WHITE[npos_w]]
        expected_adv_w = BB_F6
        self.assertEqual(computed_adv_w, expected_adv_w)

        # --------------------

        computed_capt_b = BitBoard(G.SPACE_COUNT)
        for npos_capt_b in G.LEAP_PAWN_CAPT_BLACK[npos_b]:
            computed_capt_b |= BITBOARD_SPACES[npos_capt_b]
        expected_capt_b = BB_E6 | BB_G6
        self.assertEqual(computed_capt_b, expected_capt_b)

        computed_capt_w = BitBoard(G.SPACE_COUNT)
        for npos_capt_w in G.LEAP_PAWN_CAPT_WHITE[npos_w]:
            computed_capt_w |= BITBOARD_SPACES[npos_capt_w]
        expected_capt_w = BB_E5 | BB_G5
        self.assertEqual(computed_capt_w, expected_capt_w)

        # --------------------

        computed_hop_b = BITBOARD_SPACES[G.LEAP_PAWN_HOP_BLACK[npos_b]]
        expected_hop_b = BB_F5
        self.assertEqual(computed_hop_b, expected_hop_b)

        computed_hop_w = BITBOARD_SPACES[G.LEAP_PAWN_HOP_WHITE[npos_w]]
        expected_hop_w = BB_F7
        self.assertEqual(computed_hop_w, expected_hop_w)

    def test_is_pos_on_board(self):
        NE = HexPos( 5,  5)
        N  = HexPos( 0,  5)
        NW = HexPos(-5,  0)
        SE = HexPos( 5,  0)
        S  = HexPos( 0, -5)
        SW = HexPos(-5, -5)
        CORNERS = [NE, N, NW, SE, S, SW]
        corner_tests = [G.is_pos_on_board(p) for p in CORNERS]
        self.assertTrue(all(corner_tests))

        OFF_E  = HexPos( 6,  3)
        OFF_NE = HexPos( 3,  6)
        OFF_NW = HexPos(-3,  3)
        OFF_SE = HexPos( 3, -3)
        OFF_SW = HexPos(-3, -6)
        OFF_W  = HexPos(-6, -3)
        OFFS = [OFF_E, OFF_NE, OFF_NW, OFF_SE, OFF_SW, OFF_W]
        off_tests = [not G.is_pos_on_board(p) for p in OFFS]
        self.assertTrue(all(off_tests))

    def test_rays_bishop(self):
        computed = BitBoard(G.SPACE_COUNT)
        for ray in G.RAYS_BISHOP[G.pos_to_npos(G.F6)]:
            for npos in ray:
                computed |= BITBOARD_SPACES[npos]

        expected = (BB_G7 | BB_H8  # VECS1
                | BB_H5 | BB_K4    # VECS3
                | BB_G4 | BB_H2    # VECS5
                | BB_E4 | BB_D2    # VECS7
                | BB_D5 | BB_B4    # VECS9
                | BB_E7 | BB_D8)   # VECS11

        self.assertEqual(computed, expected)

    def test_rays_queen(self):
        computed = BitBoard(G.SPACE_COUNT)
        for ray in G.RAYS_QUEEN[G.pos_to_npos(G.F6)]:
            for npos in ray:
                computed |= BITBOARD_SPACES[npos]

        expected = (
            BB_F7 | BB_F8 | BB_F9 | BB_F10 | BB_F11  # VEC0
            | BB_G7 | BB_H8                          # VEC1
            | BB_G6 | BB_H6 | BB_I6 | BB_K6 | BB_L6  # VEC2
            | BB_H5 | BB_K4                          # VEC3
            | BB_G5 | BB_H4 | BB_I3 | BB_K2 | BB_L1  # VEC4
            | BB_G4 | BB_H2                          # VEC5
            | BB_F5 | BB_F4 | BB_F3 | BB_F2 | BB_F1  # VEC6
            | BB_E4 | BB_D2                          # VEC7
            | BB_E5 | BB_D4 | BB_C3 | BB_B2 | BB_A1  # VEC8
            | BB_D5 | BB_B4                          # VEC9
            | BB_E6 | BB_D6 | BB_C6 | BB_B6 | BB_A6  # VEC10
            | BB_E7 | BB_D8                          # VEC11
            )

        self.assertEqual(computed, expected)

    def test_rays_rook(self):
        computed = BitBoard(G.SPACE_COUNT)
        for ray in G.RAYS_ROOK[G.pos_to_npos(G.F6)]:
            for npos in ray:
                computed |= BITBOARD_SPACES[npos]

        expected = (
            BB_F7 | BB_F8 | BB_F9 | BB_F10 | BB_F11  # VEC0
            | BB_G6 | BB_H6 | BB_I6 | BB_K6 | BB_L6  # VEC2
            | BB_G5 | BB_H4 | BB_I3 | BB_K2 | BB_L1  # VEC4
            | BB_F5 | BB_F4 | BB_F3 | BB_F2 | BB_F1  # VEC6
            | BB_E5 | BB_D4 | BB_C3 | BB_B2 | BB_A1  # VEC8
            | BB_E6 | BB_D6 | BB_C6 | BB_B6 | BB_A6  # VEC10
            )

        self.assertEqual(computed, expected)


if __name__ == '__main__':
    unittest.main()
