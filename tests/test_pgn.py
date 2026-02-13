#!/usr/bin/env python
# by Jay M. Coskey, 2026

from collections import Counter
import re

from bitarray import bitarray, frozenbitarray

import unittest

from src.move_info import MoveInfo
from src.pgn import Pgn


class TestPgn(unittest.TestCase):
    @classmethod
    def check_parsing_moves(cls, movetext, lang='en', is_verbose=False):
        movetext = re.sub(r"\{.*?\}", '', movetext)
        move_strs = movetext.split()
        move_sigs = []
        move_sig_map = {}
        fields_seen = bitarray(12)

        for _, move_str in enumerate(move_strs):
            move_info = Pgn.alg_to_moveinfo(move_str, lang)
            result = move_info.to_str(lang)
            if result != move_str:
                print(f'check_parsing_moves: result = {result} != {move_str} = move_str')
            assert result == move_str

            move_sig = move_info.to_move_sig()
            fields_seen |= move_sig
            if move_sig not in move_sig_map.keys():
                move_sig_map[move_sig] = [move_str]
            else:
                move_sig_map[move_sig].append(move_str)
            if is_verbose:
                print(f'move_str={move_str:<10}: move_sig={move_sig}')
            move_sigs.append(move_sig)

        move_sig_ctr = Counter(move_sigs)
        for move_sig, count in move_sig_ctr.most_common():
            move_sample = move_sig_map[move_sig][0]
            # print(f'Count={count}: Sample={move_sample:<10}: Sig={move_sig}')

    # Common formats, followed by (comparatively) rare ones
    TEST_MOVETEXT_COVERAGE = """Ng2 Bxe5 e5 fxe5 Ndf8

        Rcxf8 Qc6+ Nxf5+ R4h3 k7Q Qd2? b5? R4xe5 e5ep.
        ixk Nxf7? Ncf5+ Rhxh4+ h4+ fxe6? Qc3xBf9# f10f11=Q d8xNe8=N"""

    TEST_MOVETEXT_FOOLS_MATE = 'Qe1c3 Qe10c6 b1b2 b7b6 Bf3b1 e7e6? Qc3xBf9#'

    def test_movetext_coverage(self):
        cls = self.__class__
        movetext = cls.TEST_MOVETEXT_COVERAGE
        cls.check_parsing_moves(movetext)
        print()

    def test_movetext_fools_mate(self):
        cls = self.__class__
        movetext = cls.TEST_MOVETEXT_FOOLS_MATE
        cls.check_parsing_moves(movetext)
        print()

    def test_pgn_lines_to_game_specs(self):
        FOOLS_MATE_PGN = [line.strip() for line in """
            [Variant "Glinski"]
            [Result "1-0"]
            [Source "Glinski, W. First theories of Hexagonal Chess. Hexagonal Chess Publications, 1974."]
            [Published "1974"]

            1. Qe1c3     Qe10c6
            2. b1b2      b7b6
            3. Bf3b1     e7e6?
            4. Qc3xBf9#
            """.split('\n')]
        game_specs = Pgn.pgn_lines_to_game_specs(FOOLS_MATE_PGN)
        self.assertEqual(len(game_specs), 1)  # One game
        game_spec = game_specs[0]
        tag_pairs = game_spec[0]
        move_text = game_spec[1]

        self.assertEqual(len(tag_pairs.keys()), 4)  # 4 tag pairs
        self.assertTrue('Result' in tag_pairs.keys())
        self.assertEqual(len(move_text), 4)  # 4 lines of move text


if __name__ == '__main__':
    unittest.main()
