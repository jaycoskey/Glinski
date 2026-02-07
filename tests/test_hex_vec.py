#!/usr/bin/env python
# by Jay M. Coskey, 2006
# pylint: disable=invalid-name

import unittest

from src.hex_vec import HexVec


class TestHexVec(unittest.TestCase):
    def test_hex_vec(self):
        va = HexVec(1, 2)
        self.assertEqual(va.hex0, 1)
        self.assertEqual(va.hex1, 2)
        self.assertEqual(str(va), "<1, 2>")

        vb = HexVec(3, 4)
        self.assertEqual(vb.hex0, 3)
        self.assertEqual(vb.hex1, 4)
        self.assertEqual(str(vb), "<3, 4>")

        self.assertEqual(va + vb, HexVec(4, 6))
        self.assertEqual(va - vb, HexVec(-2, -2))
        self.assertEqual(2 * va, HexVec(2, 4))
        self.assertEqual(va * 2, HexVec(2, 4))

    def test_hex_vec_sums(self):
        zero = HexVec(0, 0)

        v0 = HexVec(0, 1)
        v2 = HexVec(1, 1)
        v4 = HexVec(1, 0)
        v6 = HexVec(0, -1)
        v8 = HexVec(-1, -1)
        v10 = HexVec(-1, 0)

        v1 = HexVec(1, 2)
        v3 = HexVec(2, 1)
        v5 = HexVec(1, -1)
        v7 = HexVec(-1, -2)
        v9 = HexVec(-2, -1)
        v11 = HexVec(-1, 1)

        self.assertEqual(v0 + v6, zero)
        self.assertEqual(v1 + v7, zero)
        self.assertEqual(v2 + v8, zero)
        self.assertEqual(v3 + v9, zero)
        self.assertEqual(v4 + v10, zero)
        self.assertEqual(v5 + v11, zero)

        self.assertEqual(v0 + v4 + v8, zero)
        self.assertEqual(v1 + v5 + v9, zero)
        self.assertEqual(v2 + v6 + v10, zero)
        self.assertEqual(v3 + v7 + v11, zero)


if __name__ == "__main__":
    unittest.main()
