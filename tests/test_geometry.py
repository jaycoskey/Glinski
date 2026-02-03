#!/usr/bin/env python
# by Jay M. Coskey, 2026

from src.geometry import Geometry as G
from src.hex_pos import HexPos
from src.hex_vec import HexVec

import unittest


class TestGeometry(unittest.TestCase):
    def test_geometry_constants(self):
        self.assertEqual(G.SPACES_COUNT, 91)

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

    def test_hexpos_hexvec_add_vecs12(self):
        self.assertEqual(sum(G.VECS_12, G.ZERO), G.ZERO)

    def test_hexpos_hexvec_add_knights(self):
        center = HexPos(5, 5)
        pos = center
        for k in range(len(G.VECS_KNIGHT)):
            kvec = G.VECS_KNIGHT[k]
            pos = pos + kvec
            if k < 11:
                self.assertNotEqual(pos, center)
        self.assertEqual(pos, center)  # Back to where we started

    def test_hexpos_hexvec_add_pawns(self):
        vec_bp = sum(G.VECS_PAWN_BLACK_CAPT, start=HexVec(0, 0))
        assert(vec_bp == G.VECS_PAWN_BLACK_ADV[0])

        vec_wp = sum(G.VECS_PAWN_WHITE_CAPT, start=HexVec(0, 0))
        assert(vec_wp == G.VECS_PAWN_WHITE_ADV[0])


if __name__ == '__main__':
    unittest.main()
