#!/usr/bin/env python
# by Jay M. Coskey, 2026

import unittest

from src.hex_pos import HexPos
from src.hex_vec import HexVec


class Test_HexPos(unittest.TestCase):
    def test_hex_pos_clock(self):
        center = HexPos(0, 0)

        # Board corners
        nw = HexPos(-5, 0)
        sw = HexPos(-5, -5)
        n = HexPos(0, 5)
        s = HexPos(0, -5)
        ne = HexPos(5, 5)
        se = HexPos(5, 0)

        # Clock directions
        v0 = HexVec(0, 1)
        v2 = HexVec(1, 1)
        v4 = HexVec(1, 0)
        v6 = HexVec(0, -1)
        v8 = HexVec(-1, -1)
        v10 = HexVec(-1, 0)

        # Spokes, addition
        self.assertEqual(center + 5 * v0, n)
        self.assertEqual(center + 5 * v2, ne)
        self.assertEqual(center + 5 * v4, se)
        self.assertEqual(center + 5 * v6, s)
        self.assertEqual(center + 5 * v8, sw)
        self.assertEqual(center + 5 * v10, nw)

        # Spokes, subtraction
        self.assertEqual(n - center, 5 * v0)
        self.assertEqual(ne - center, 5 * v2)
        self.assertEqual(se - center, 5 * v4)
        self.assertEqual(s - center, 5 * v6)
        self.assertEqual(sw - center, 5 * v8)
        self.assertEqual(nw - center, 5 * v10)

        # Wheel
        self.assertEqual(n + 5 * v4, ne)
        self.assertEqual(ne + 5 * v6, se)
        self.assertEqual(se + 5 * v8, s)
        self.assertEqual(s + 5 * v10, sw)
        self.assertEqual(sw + 5 * v0, nw)

        # Meander
        v1 = HexVec(1, 2)
        v5 = HexVec(1, -1)
        v9 = HexVec(-2, -1)
        self.assertEqual(center + 2*v0  +  2*v5  +  3*v9  +  5*v2  -  v1, center)
        #                (0,0)  + <0,2> + <2,-2> + <-6,-3>+ <5,5>  - <1,2>

    # GREP: Coordinate choice
    def test_hex_pos_rank(self):
        self.assertEqual(HexPos(0, 0).rank(), 6)

        self.assertEqual(HexPos(-5, 0).rank(), 6)
        self.assertEqual(HexPos(-5, -5).rank(), 1)
        self.assertEqual(HexPos(0, 5).rank(), 11)
        self.assertEqual(HexPos(0, -5).rank(), 1)
        self.assertEqual(HexPos(5, 5).rank(), 6)
        self.assertEqual(HexPos(5, 0).rank(), 1)

    def test_hex_pos_str(self):
        center = HexPos(0, 0)
        self.assertEqual(str(center), "(0, 0)")


if __name__ == "__main__":
    unittest.main()
