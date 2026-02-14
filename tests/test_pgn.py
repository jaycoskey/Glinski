#!/usr/bin/env python
# by Jay M. Coskey, 2026

from collections import Counter
import re

from bitarray import bitarray, frozenbitarray

import unittest

from src.move_spec import MoveSpec
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
            move_spec = Pgn.alg_to_move_spec(move_str, lang)
            result = move_spec.to_str(lang)
            if result != move_str:
                print(f'check_parsing_moves: result = {result} != {move_str} = move_str')
            assert result == move_str

            move_sig = move_spec.to_move_sig()
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
    COVERAGE_MOVE_TEXT = """Ng2 Bxe5 e5 fxe5 Ndf8

        Rcxf8 Qc6+ Nxf5+ R4h3 k7Q Qd2? b5? R4xe5 e5ep.
        ixk Nxf7? Ncf5+ Rhxh4+ h4+ fxe6? Qc3xBf9# f10f11=Q d8xNe8=N"""

    FOOLS_MATE_MOVE_TEXT = 'Qe1c3 Qe10c6 b1b2 b7b6 Bf3b1 e7e6? Qc3xBf9#'

    FOOLS_MATE_PGN = [line for line in [line.strip() for line in """
        [Variant "Glinski"]
        [Result "1-0"]
        [Source "Glinski, W. First theories of Hexagonal Chess. Hexagonal Chess Publications, 1974."]
        [Published "1974"]

        1. Qe1c3 Qe10c6 2. b1b2 b7b6 3. Bf3b1 e7e6? 4. Qc3xBf9#
        """.split('\n')] if line != '']

    def test_movetext_coverage(self):
        cls = self.__class__
        cls.check_parsing_moves(cls.COVERAGE_MOVE_TEXT)
        print()

    def test_movetext_fools_mate(self):
        cls = self.__class__
        cls.check_parsing_moves(cls.FOOLS_MATE_MOVE_TEXT)
        print()

    def test_pgn_lines_to_game_specs(self):
        cls = self.__class__
        game_specs = Pgn.pgn_lines_to_game_specs(cls.FOOLS_MATE_PGN)
        self.assertEqual(len(game_specs), 1)  # One game
        game_spec = game_specs[0]
        tag_pairs = game_spec[0]
        move_text = game_spec[1]

        self.assertEqual(len(tag_pairs.keys()), 4)  # 4 tag pairs
        self.assertTrue('Result' in tag_pairs.keys())
        self.assertEqual(len(move_text), 1)  # 1 line of move text

    def test_pgn_lines_to_games(self):
        cls = self.__class__
        games = Pgn.pgn_lines_to_games(cls.FOOLS_MATE_PGN)
        self.assertEqual(len(games), 1)
        game = games[0]
        self.assertEqual(len(game.get_game_tag_pairs()), 4)
        self.assertEqual(game.board.get_halfmove_count(), 7)
        #
        # Not equal, since the PGN parsing doesn't yet carry over move eval strings.
        # self.assertEqual(game.get_pgn_str(), '\n'.join(cls.FOOLS_MATE_PGN))


if __name__ == '__main__':
    unittest.main()
