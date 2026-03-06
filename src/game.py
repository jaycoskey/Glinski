#!/usr/bin/env python
# by Jay M. Coskey, 2026

from collections import OrderedDict
from typing import Tuple

from src.board import Board
from src.controller import Controller
from src.controller import HumanPlayer, RandomPlayer
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
    def __init__(self, **kwargs):
        self.attrs: OrderedDict[str, str] = None
        self.board: Board = None
        self.controllers: Dict[Player, Controller] = None

        for option, val in kwargs.items():
            if option == 'fen':
                # TODO
                continue
            if option == 'layout_dict':
                # TODO: Use layout_dict to initialize Board
                continue
            if option == 'pgn_path':
                # TODO: Read in PGN file from pgn_path -> GameSpec, etc.
                continue
            if option == 'pgn_text':
                # TODO: Initialize Game with pgn_text
                continue
            if option == 'players':
                valid_chars = 'hr'
                CHAR_TO_CONTROLLER = {
                        'h': HumanPlayer,
                        'r': RandomPlayer,
                        }
                if (len(val) != 2 or val[0] not in valid_chars
                        or val[1] not in valid_chars):
                    print('Game constructor: players=<w><b>, where <w> and <b>')
                    print('indicate which Controller is used for each Player:')
                    print('  * "h" (for a Human player)')
                    print('  * "r" (for a Random computer player).')
                    continue
                self.controllers: Dict[Player, Controller] = {}
                self.controllers[Player.White] = CHAR_TO_CONTROLLER[val[0]]
                self.controllers[Player.Black] = CHAR_TO_CONTROLLER[val[1]]

        if self.attrs is None:
            self.attrs = OrderedDict[str, str]()
        if self.board is None:
            self.board = Board()
        if self.controllers is None:
            self.controllers = {
                    Player.Black: RandomPlayer,
                    Player.White: RandomPlayer
                    }

    # Added for testing.
    # Not to be used for printing game state for a text-based human player.
    def __str__(self):
        # attrs_str = ('{'
        #         + '; '.join([f'{k}=>"{v}"' for k,v in self.attrs.items()])
        #         + ' }')
        # board_str = self.board.get_print_str()
        piece_count = len([1 for piece in self.board.pieces if piece is not None])
        move_count = len([1 for move in self.board.history_move if move is not None])
        result = f'<<{len(self.attrs)} attrs, {piece_count} pieces, {move_count} moves>>'
        return result

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
        if self.game_state == GameState.WinBlack:
            return "0-1"
        if self.game_state == GameState.WinWhite:
            return "1-0"
        if self.game_state == GameState.WinStalemateBlack:
            return "1/4-3/4"
        if self.game_state == GameState.WinStalemateWhite:
            return "3/4-1/4"
        if self.game_state == GameState.Draw:
            return "1/2-1/2"
        return "(Score TBD)"

    def get_scores_vals(self) -> Tuple[float, float]:
        if self.game_state == GameState.WinBlack:
            return (0, 1)
        if self.game_state == GameState.WinWhite:
            return (1, 0)
        if self.game_state == GameState.WinStalemateBlack:
            return (0.25, 0.75)
        if self.game_state == GameState.WinStalemateWhite:
            return (0.75, 0.25)
        if self.game_state == GameState.Draw:
            return (0.5, 0.5)
        raise RuntimeError('Should not get score values fro unfinished game')

    def play(self):
        self.board.set_game_state(GameState.InPlay)
        while self.game_state == GameState.InPlay:  # Game loop
            controller = self.controllers[self.board.cur_player]
            choice = controller.choose_move(self.board)
            if isinstance(choice, Move):
                self.board.move_make(choice)
                continue
            elif isinstance(choice, MoveAlternative):
                if choice == MoveAlternative.ClaimNonProgress50:
                    self.board.set_game_state(GameState.Draw)
                    break
                if choice == MoveAlternative.ClaimRepetition3x:
                    self.board.set_game_state(GameState.Draw)
                    break
                if choice == MoveAlternative.OfferDraw:
                    opp_controller = self.controllers[self.board.cur_player.opponent]
                    response = opp_controller.do_accept_offer_draw()
                    if response:
                        self.board.set_game_state(GameState.Draw)
                    continue
                if choice == MoveAlternative.Resign:
                    game_state = (GameState.WinBlack
                            if self.board.cur_player == Player.Black
                            else GameState.WinWhite)
                    self.board.set_game_state(game_state)
                    break
            else:
                ValueError('Unknown type returned from Controller.choose_move()')

        # TODO: Notify players of outcome.
        # TODO: Refactor this Game summary into a method.
        game_state = self.board.game_state
        if game_state == GameState.Draw:
            print('Game is a draw.')
        elif game_state == GameState.WinBlack:
            print('Black won.')
        elif game_state == GameState.WinBlackStalemate:
            print('Black stalemated White.')
        elif game_state == GameState.WinWhite:
            print('White won.')
        elif game_state == GameState.WinWhiteStalemate:
            print('White stalemated Black.')

    def send_player_notification(self, move: Move):
        pass

    def set_attributes(self, attrs: OrderedDict[str, str]):
        for k, v in attrs.items():
            self.attrs[k] = v

if __name__ == '__main__':
    g = Game(players='rr')
    g.play()

