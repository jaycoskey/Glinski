#!/usr/bin/env python
# by Jay M. Coskey, 2026

from collections import OrderedDict
from typing import Tuple

from src.board import Board
# TODO: from src.controller import Controller
# TODO: from src.controller import RandomPlayer, TextPlayer
from src.game_state import GameState
from src.move import Move
from src.player import Player


# Note three possible roles for a class Game.
#   (a) Complete state: A Game is played from beginning to end.
#       from loaded PGN file.
#   (b) Partial state: A Game is loaded from FEN, then play ensues.
#   (c) Minimal state: A Game is created to solve a mate-in-2
#       puzzle, where there is no need to track non-progress or
#       board duplication.
class Game:
    # TODO: Add various means of initialization: fen, pgn_path, pgn_str.
    # TODO: Add user/controller interaction via Controller classes:
    #       RandomUser, TextUser, etc.
    def __init__(self, fen=None, pgn_path=None, pgn_str=None):
        self.attrs: OrderedDict[str, str] = OrderedDict[str, str]()
        self.board: Board = Board()
        # TODO: self.controllers: Dict[Player, Controller]

        # self.controllers[Player.Black] = RandomPlayer()
        # self.controllers[Player.White] = RandomPlayer()

    # Added for testing.
    # Not to be used for printing game state for a text-based human player.
    def __str__(self):
        attrs_str = ('{'
                + '; '.join([f'{k}=>"{v}"' for k,v in self.attrs.items()])
                + ' }')
        board_str = self.board.get_print_str()
        return attrs_str + '\n' + board_str

    @property
    def game_state(self):
        return self.board.game_state

    def get_game_tag_pairs_str(self) -> str:
        attr_strs = [f'[{k} "{v}"]' for k, v in self.attrs.items()]
        return '\n'.join(attr_strs)

    def get_game_move_text(self):
        result = ''
        for k in range(1, len(self.board.history_move)):
            if (k % 2) == 1:
                turn_num = (k + 1) >> 1
                result += f' {turn_num}.'
            result += ' ' + str(self.board.history_move[k])
        return result

    def get_game_tag_pairs(self):
        return self.attrs.copy()

    def get_pgn_str(self):
        return self.get_game_tag_pairs_str() + self.get_game_move_text()

    def get_scores_str(self):
        if self.game_state == GameState.Win_Black:
            return "0-1"
        if self.game_state == GameState.Win_White:
            return "1-0"
        if self.game_state == GameState.Stalemate_Win_Black:
            return "1/4-3/4"
        if self.game_state == GameState.Stalemate_Win_White:
            return "3/4-1/4"
        if self.game_state == GameState.Draw:
            return "1/2-1/2"
        return "(Score TBD)"

    def get_scores_vals(self) -> Tuple[float, float]:
        if self.game_state == GameState.Win_Black:
            return (0, 1)
        if self.game_state == GameState.Win_White:
            return (1, 0)
        if self.game_state == GameState.Stalemate_Win_Black:
            return (0.25, 0.75)
        if self.game_state == GameState.Stalemate_Win_White:
            return (0.75, 0.25)
        if self.game_state == GameState.Draw:
            return (0.5, 0.5)
        raise RuntimeError('Should not get score values fro unfinished game')

    def play(self):
        pass
        # TODO: Implement game play loop
        # assert self.board.cur_player == Player.White  # In case it wasn't already set
        # while self.game_state == GameState.InPlay:
        #     controller = self.controllers[game.cur_player]
        #     move = controller.get_move(self.game.board)
        #     self.board.move_make(move)
        # TODO: Print game result info. Notify players.

    def send_player_notification(self, move: Move):
        pass

    def set_attributes(self, attrs: OrderedDict[str, str]):
        for k, v in attrs.items():
            self.attrs[k] = v
