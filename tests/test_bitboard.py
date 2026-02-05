#!/usr/bin/env python
# by Jay M. Coskey, 2026

import unittest

from src.bitboard import *
from src.bitboard import npos_to_bb


class TestBitboard(unittest.TestCase):
    def test_bitboard_files(self):
        # Verify that the files are pairwise disjoint
        for i in range(len(BITBOARD_FILES)):
            bbfi = BITBOARD_FILES[i]
            for j in range(i + 1, len(BITBOARD_FILES)):
                bbfj = BITBOARD_FILES[j]
                self.assertEqual((bbfi & bbfj).count(), 0)

    def test_bitboard_edges(self):
        for i in range(len(BITBOARD_EDGES)):
            bbei = BITBOARD_EDGES[i]
            for j in range(i + 1, len(BITBOARD_EDGES)):
                bbej = BITBOARD_EDGES[j]
                intersection = bbei & bbej
                intersection_count = (bbei & bbej).count()
                if intersection.count() > 0:
                    self.assertTrue((intersection & BB_CORNERS).count(), intersection.count())
                    self.assertTrue(intersection_count == 1)

    def test_bitboard_npos_to_bb(self):
        self.assertEqual(npos_to_bb(0), BB_A6)
        self.assertEqual(npos_to_bb(5), BB_A1)
        self.assertEqual(npos_to_bb(40), BB_F11)
        self.assertEqual(npos_to_bb(45), BB_F6)
        self.assertEqual(npos_to_bb(50), BB_F1)
        self.assertEqual(npos_to_bb(85), BB_L6)
        self.assertEqual(npos_to_bb(90), BB_L1)

    def test_bitboard_rings(self):
        self.assertEqual(BB_RING0.count(), 1)
        self.assertEqual(BB_RING1.count(), 6)
        self.assertEqual(BB_RING2.count(), 12)
        self.assertEqual(BB_RING3.count(), 18)
        self.assertEqual(BB_RING4.count(), 24)
        self.assertEqual(BB_RING5.count(), 30)

        for i in range(len(BITBOARD_RINGS)):
            bbri = BITBOARD_RINGS[i]
            for j in range(i + 1, len(BITBOARD_RINGS)):
                bbrj = BITBOARD_RINGS[j]
                intersection = BITBOARD_RINGS[i] & BITBOARD_RINGS[j]
                self.assertEqual(intersection.count(), 0)

    def test_bitboard_space_colors(self):
        self.assertEqual((BB_SPACES_LIGHT & BB_SPACES_MEDIUM).count(), 0)
        self.assertEqual((BB_SPACES_LIGHT & BB_SPACES_DARK).count(), 0)
        self.assertEqual((BB_SPACES_MEDIUM & BB_SPACES_DARK).count(), 0)

    def test_bitboard_wefts(self):
        # Verify that the wefts are pairwise disjoint
        for i in range(len(BITBOARD_WEFTS)):
            bbwi = BITBOARD_WEFTS[i]
            for j in range(i + 1, len(BITBOARD_WEFTS)):
                bbwj = BITBOARD_WEFTS[j]
                self.assertFalse((bbwi & bbwj).any())


if __name__ == '__main__':
    unittest.main()
