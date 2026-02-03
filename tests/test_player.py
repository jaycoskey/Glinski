#!/usr/bin/env python
# by Jay M. Coskey, 2026

import unittest

from src.player import Player


class TestPlayer(unittest.TestCase):
    def test_player(self):
        b1 = Player.Black
        w1 = Player.White

        b2 = w1.opponent()
        w2 = b1.opponent()

        self.assertEqual(b1, b2)
        self.assertEqual(w1, w2)

        self.assertNotEqual(b1, w2)
        self.assertNotEqual(w1, b2)


if __name__ == '__main__':
    unittest.main()
