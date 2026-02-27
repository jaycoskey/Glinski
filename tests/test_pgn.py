#!/usr/bin/env python
# by Jay M. Coskey, 2026

from collections import Counter
import os
import re

from bitarray import bitarray, frozenbitarray

import unittest

from src.move_spec import MoveSpec
from src.pgn import Pgn


class TestPgn(unittest.TestCase):
    @classmethod
    def check_parsing_moves(cls, move_text: str, lang='en', is_verbose=False):
        move_text = re.sub("\{.*?\}", '', move_text)
        move_strs = move_text.split()
        move_sigs = []  # Bitarrays reflecting move parsing coverage
        move_sig_map = {}
        fields_seen = bitarray(12)

        for _, move_str in enumerate(move_strs):
            move_spec = Pgn.move_text_to_move_spec(move_str, lang)
            move_sig = move_spec.to_move_sig()
            fields_seen |= move_sig
            if move_sig not in move_sig_map.keys():
                move_sig_map[move_sig] = [move_str]
            else:
                move_sig_map[move_sig].append(move_str)
            if is_verbose:
                print(f'move_str={move_str:<10}: move_sig={move_sig}')
            move_sigs.append(move_sig)

        if is_verbose:
            move_sig_ctr = Counter(move_sigs)
            for move_sig, count in move_sig_ctr.most_common():
                print(f'Move sig appearances={count}: {move_sig}: Sample={move_sig_map[move_sig][0]}')

    # Distinct "parsing flavors" of formats. More common,
    # followed by less common, and rare ones.
    COVERAGE_MOVE_TEXT = """Ng2 Bxe5 e5 fxe5 Ndf8

        Rcxf8 Qc6+ Nxf5+ R4h3 k7Q Qd2? b5? R4xe5 e5ep.
        ixk Nxf7? Ncf5+ Rhxh4+ h4+ fxe6? Qc3xBf9# f10f11=Q d8xNe8=N

        gxh5+ c1Q+
        """

    FOOLS_MATE_MOVE_TEXT = 'Qe1c3 Qe10c6 b1b2 b7b6 Bf3b1 e7e6? Qc3xBf9#'

    FOOLS_MATE_PGN = [line for line in [line.strip() for line in """
        [Variant "Glinski"]
        [Result "1-0"]
        [Source "Glinski, W. First theories of Hexagonal Chess. Hexagonal Chess Publications, 1974."]
        [Published "1974"]

        1. Qe1c3 Qe10c6 2. b1b2 b7b6 3. Bf3b1 e7e6? 4. Qc3xBf9#
        """.split('\n')] if line != '']

    def test_move_specs(self):
        fname = os.getenv('GLINSKI_HOME') + '/data/pgn/HexagonalChessTournaments_hu.pgn'
        pgn_lines = Pgn.get_pgn_lines(fname)
        tag_filter = {'GameID': '13'}
        # tag_filter = None
        game_specs = Pgn.pgn_lines_to_game_specs(pgn_lines, tag_filter)
        move_texts = []
        move_specs = []
        move_sigs = set()

        for game_spec in game_specs:
            game_move_texts = Pgn.move_lines_to_move_texts(game_spec[1])
            game_move_texts.extend(Pgn.move_lines_to_move_texts(game_spec[1]))
            for move_text in move_texts:
                if move_text in ['0-1', '1-0', 'draw', 'remi', 'ź-ź', '...']:
                    continue
                move_spec = Pgn.move_text_to_move_spec(move_text, lang='hu')

    def test_move_text_coverage(self):
        cls = self.__class__
        cls.check_parsing_moves(cls.COVERAGE_MOVE_TEXT)
        print()

    def test_move_text_fools_mate(self):
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

        self.assertEqual(len(tag_pairs), 4)  # 4 tag pairs
        self.assertTrue('Result' in tag_pairs.keys())
        self.assertEqual(len(move_text), 1)  # 1 line of move text

    def test_pgn_lines_to_games(self):
        is_verbose = False
        pgn_dir = '/data/pgn/'
        pgn_fname = 'HexagonalChessTournaments_hu.pgn'
        fname = os.getenv('GLINSKI_HOME') + pgn_dir + pgn_fname
        pgn_lines = Pgn.get_pgn_lines(fname)
        tag_filter = None
        game_specs = Pgn.pgn_lines_to_game_specs(pgn_lines, tag_filter)
        games = []
        for game_spec in game_specs:
            game = Pgn.game_spec_to_game(game_spec, 'hu')
            games.append(game)
            if is_verbose:
                attrs = game_spec[0]
                game_id = ' ' + attrs['GameID'] if 'GameID' in attrs else ''
                print(f'Final board layout of Game{game_id}:')
                game.board.print()
        if is_verbose:
            print(f'Number of games found: {len(games)}')

    def test_fools_mate_to_game(self):
        cls = self.__class__
        game_specs = Pgn.pgn_lines_to_game_specs(cls.FOOLS_MATE_PGN)
        self.assertEqual(len(game_specs), 1)
        game_spec = game_specs[0]
        game = Pgn.game_spec_to_game(game_spec)
        self.assertEqual(len(game.get_game_tag_pairs()), 4)
        self.assertEqual(game.board.get_halfmove_count(), 7)

        # Not equal, since the PGN parsing doesn't yet carry over MoveEval info.
        # self.assertEqual(game.get_pgn_str(), '\n'.join(cls.FOOLS_MATE_PGN))


if __name__ == '__main__':
    unittest.main()
