#!/usr/bin/env python
# by Jay M. Coskey, 2026
# pylint: disable=import-error, invalid-name, fixme, line-too-long
# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches, too-many-locals, too-many-statements

from abc import ABC
# import gettext
from random import randint
import re
from typing import Union

from src.board import Board
from src.geometry import Geometry as G
from src.move import Move
from src.move_alternative import MoveAlternative


# Note: This class is stateless. It does not contain instance data.
class Controller(ABC):
    @classmethod
    def choose_move(cls, board: Board) -> Union[Move, MoveAlternative]:
        pass

    @classmethod
    def do_accept_offer_draw(cls, board: Board) -> bool:
        pass


# TODO: Support human play through a GUI.
# TODO: Support play between two human players at different devices.
class HumanPlayer(Controller):
    @classmethod
    def choose_move(cls, board: Board) -> Union[Move, MoveAlternative]:
        board.print()

        CMD_PROMPT_PREFACE_0_EN = 'Input "help <topic>" or "move <UCI_format>", or one of:'
        CMD_PROMPT_PREFACE_1_EN = '  board, draw, history, offer, resign, undo.'

        CMD_HELP_EN = 'help'

        CMD_BOARD_EN = 'board'
        CMD_DRAW_EN = 'draw'
        CMD_HISTORY_EN = 'history'
        CMD_MOVE_EN = 'move'
        CMD_OFFER_EN = 'offer'
        CMD_RESIGN_EN = 'resign'
        CMD_UNDO_EN = 'undo'

        CMDS_VALID_EN = [CMD_HELP_EN,
                CMD_BOARD_EN, CMD_DRAW_EN, CMD_HISTORY_EN, CMD_MOVE_EN,
                CMD_OFFER_EN, CMD_RESIGN_EN, CMD_UNDO_EN, '?', '??', '???']

        CMD_ERROR_UNRECOGNIZED_CMD = 'Unrecognized command'
        CMD_ERROR_UNRECOGNIZED_CMDS = 'Unrecognized commands'

        CMD_BOARD_SUBCMD_ASCII_EN = 'ascii'
        CMD_BOARD_SUBCMD_FEN_EN = 'fen'
        CMD_BOARD_SUBCMD_SVG_EN = 'svg'
        CMD_BOARD_SUBCMD_UNICODE_EN = 'unicode'

        CMD_OFFER_CONFIRMATION_EN = 'Do you accept the offer of a draw? (Y/n): '

        HELP_0_EN = 'Available help commands:'
        HELP_1_EN = '  * "help": Prints this message.'
        HELP_2_EN = '  * "help board": Explains how to print out the board, or save an SVG version to disk.'
        HELP_2_EN = '  * "help draw": Explains how to claims a draw based on the 50-move rule or 3x board replication.'
        HELP_2_EN = '  * "help history": Explains how to print the Game history in PGN format.'
        HELP_3_EN = '  * "help move": Explains how to express which move has been chosen.'
        HELP_3_EN = '  * "help offer": Explains how to offer the opponent a draw.'
        HELP_4_EN = '  * "help resign": Explains how to resign.'
        HELP_5_EN = '  * "help undo": Explains how to roll back the game to this Player\'s previous move.'

        HELP_BOARD_0_EN = 'The command "board <format>" prints the board, where format is "ascii" or "unicode".'

        HELP_BOARD_ERROR_ARGS_0_EN = 'A second argument is required to specify the format of the board'
        HELP_BOARD_ERROR_ARGS_1_EN = 'Valid sub-commands: ascii, unicode, svg'

        HELP_DRAW_0_EN = 'The command "draw <number>" is used to claim a draw. It has two sub-commands:'
        HELP_DRAW_1_EN = '  * "3" is used to claim a draw based on 3-fold replication of a board position'
        HELP_DRAW_2_EN = '  * "50" is used to claim a draw based on the 50-move rule.'

        HELP_DRAW_ERROR_UNAVAILABLE_0_EN = 'No basis for a draw is available.'

        HELP_HISTORY_0_EN = 'The command "history" prints the move of the Game in PGN format.'

        HELP_MOVE_0_EN = 'The command "move <movetext>" makes a move, where "movetext" is in UCI format,'
        HELP_MOVE_1_EN = 'which uses the form <from_file><from_rank><to_file><to_rank><promoted_type>, where:'
        HELP_MOVE_2_EN = '  * "from_file" is the file (i.e., column) that the Player is moving a piece *from*;'
        HELP_MOVE_3_EN = '  * "from_rank" is the rank that the Player is moving a piece *from*;'
        HELP_MOVE_4_EN = '  * "to_file" is the file (i.e., column) that the Player is moving a piece *to*;'
        HELP_MOVE_5_EN = '  * "to_rank" is the rank that the Player is moving a piece *to*;'
        HELP_MOVE_6_EN = '  * In cases of Pawn promotion, "promoted_type" is type the Pawn is being promoted to.'

        HELP_OFFER_0_EN = 'The command "offer" has only one (optional) sub-command: draw.'

        HELP_RESIGN_0_EN = 'The command "resign" resigns the game. It does not require confirmation.'

        HELP_UNDO_0_EN = 'The command "undo" undoes both your opponents last move '
        HELP_UNDO_1_EN = 'and then your last move, making it your turn again.'
        HELP_UNDO_2_EN = 'Note that there is not (currently) any "redo" command.'

        def print_strs(*strs):
            for s in strs:
                print(s)

        partial_to_full_command = {}
        for valid_cmd in CMDS_VALID_EN:
            for k in range(1, len(valid_cmd) - 1):
                partial_to_full_command[valid_cmd[0:k]] = valid_cmd

        is_move_selection_pending = True
        # Note: Iterate until either the choice of a Move or a MoveAlternative.
        while is_move_selection_pending:
            print_strs(CMD_PROMPT_PREFACE_0_EN, CMD_PROMPT_PREFACE_1_EN)
            response = input(f'glinski:{board.cur_player.name}> ')
            cmds = response.split()
            if cmds[0] not in CMDS_VALID_EN:
                if cmds[0] in partial_to_full_command:
                    cmds[0] = partial_to_full_command[cmds[0]]
                else:
                    print(f'{CMD_ERROR_UNRECOGNIZED_CMDS}: {cmds}')
            cmd = cmds[0]

            if cmd == CMD_HELP_EN or cmd[0] == '?':
                if len(cmds) == 1:
                    print_strs(HELP_0_EN, HELP_1_EN, HELP_2_EN,
                            HELP_3_EN, HELP_4_EN, HELP_5_EN)
                    continue
                if cmds[1] == CMD_BOARD_EN:
                    print_strs(HELP_BOARD_0_EN)
                    continue
                if cmds[1] == CMD_DRAW_EN:
                    print_strs(HELP_DRAW_0_EN, HELP_DRAW_1_EN, HELP_DRAW_2_EN)
                    continue
                if cmds[1] == CMD_HISTORY_EN:
                    print_strs(HELP_HISTORY_0_EN)
                    continue
                if cmds[1] == CMD_MOVE_EN:
                    print_strs(HELP_MOVE_0_EN, HELP_MOVE_1_EN,
                            HELP_MOVE_2_EN, HELP_MOVE_3_EN, HELP_MOVE_4_EN,
                            HELP_MOVE_5_EN, HELP_MOVE_6_EN)
                    continue
                if cmds[1] == CMD_OFFER_EN:
                    print_strs(HELP_OFFER_0_EN)
                    continue
                if cmds[1] == CMD_RESIGN_EN:
                    print_strs(HELP_RESIGN_0_EN)
                    continue
                if cmds[1] == CMD_UNDO_EN:
                    print_strs(HELP_UNDO_0_EN, HELP_UNDO_1_EN,
                            HELP_UNDO_2_EN)
                    continue
                print('Help sub-command unrecognized')
                continue

            # TODO: Implement other board sub-commands: jpg, png, video
            if cmd == CMD_BOARD_EN:
                if len(cmds) == 1:
                    print_strs(HELP_BOARD_ERROR_ARGS_0_EN,
                            HELP_BOARD_ERROR_ARGS_1_EN)
                    continue
                if len(cmds) == 2:
                    if cmds[1] == CMD_BOARD_SUBCMD_ASCII_EN:
                        board.print_ascii()
                        continue
                    if cmds[1] == CMD_BOARD_SUBCMD_UNICODE_EN:
                        board.print_unicode()
                        continue
                    if cmds[1] == CMD_BOARD_SUBCMD_FEN_EN:
                        fen = board.get_fen()
                        print(fen)
                        continue
                    print(f'Unrecognized board sub-command: {cmds[1]}')
                if cmds[1] == CMD_BOARD_SUBCMD_SVG_EN:
                    if len(cmds) != 4:
                        print('Wrong number of "board svg" options.')
                        print('There should be 2: output_directory and file_basename')
                    out_dir = cmds[2]
                    base_name = cmds[3]
                    board.svg_write(out_dir, base_name)
                    continue
                if len(cmds) > 2:
                    print(f'Too many board sub-commands: {cmds[1:]}')
                    continue
                # If we've reached here, then len(cmds) == 2
                continue  # Method still waiting for selection.
            if cmd == CMD_DRAW_EN:
                # TODO: Include handling of sub-command specifying basis for claim.
                if board.is_50_move_rule_triggered:
                    return MoveAlternative.ClaimNonProgress50
                if board.is_repetition_3x:
                    return MoveAlternative.ClaimRepetition3x
                print(HELP_DRAW_ERROR_UNAVAILABLE_0_EN)
                continue
            if cmd == CMD_HISTORY_EN:
                self.print_pgn_turns()
                continue
            if cmd == CMD_MOVE_EN:
                uci = cmds[1]
                match = re.match(r'(\w)(\d+)(\w)(\d+)(\w?)', uci)
                if not match:
                    print(f'Move text has invalid syntax: {uci}')
                    continue
                try:
                    fr_file = match.group(1)
                    fr_rank = match.group(2)
                    to_file = match.group(3)
                    to_rank = match.group(4)
                    promo_str = match.group(5)

                    print(f'move is {fr_file}{fr_rank}-{to_file}{to_rank}')
                    print(f'move is {fr_file}{fr_rank}-{to_file}{to_rank}')
                    assert(fr_file in G.FILE_CHARS)
                    fr_hex0 = G.FILE_CHAR_TO_HEX0[fr_file]
                    assert(1 <= int(fr_rank) <= G.RANK_COUNT_PER_FILE[fr_hex0] + 5)

                    assert(to_file in G.FILE_CHARS)
                    to_hex0 = G.FILE_CHAR_TO_HEX0[to_file]
                    assert(1 <= int(to_rank) <= G.RANK_COUNT_PER_FILE[to_hex0] + 5)
                except Exception as e:
                    print(f'Move text has invalid values: {uci}')
                    print(f'Exception: {e}')
                    continue
                fr_alg = fr_file + fr_rank
                fr_npos = G.alg_to_npos(fr_alg)
                try:
                    fr_piece = board.pieces[fr_npos]
                    assert fr_piece and fr_piece.player == board.cur_player
                except Exception as e:
                    print(f'Error: Player has no Piece to move at {fr_alg}: {e}.')
                    continue
                to_npos = G.alg_to_npos(to_file + to_rank)
                promo_pt = PieceType.from_symbol(promo_str) if promo_str else None
                move = Move(fr_npos, to_npos, promo_pt)
                return move
            if cmd == CMD_OFFER_EN:
                return MoveAlternative.OfferDraw
            if cmd == CMD_RESIGN_EN:
                return MoveAlternative.Resign
            if cmd == CMD_UNDO_EN:
                # TODO: Notify opponent (human or stateful AI)
                board.move_undo()  # Undo the opponents most recent move.
                board.move_undo()  # Undo this player's most recent move.
                continue
            assert False  # Should not reach here: Cmd validated @ top of loop.

    @classmethod
    def do_accept_offer_draw(cls, board: Board) -> bool:
        response = input(CMD_OFFER_CONFIRMATION_EN)
        return response[0].upper() == 'Y'


class RandomPlayer(Controller):
    @classmethod
    def choose_move(cls, board: Board) -> Union[Move, MoveAlternative]:
        moves = board.get_moves_legal()
        assert moves, f'RandomPlayer {board.cur_player.name} has no moves'
        choice_index = randint(0, len(moves) - 1)
        print('*', end='')
        return moves[choice_index]

    @classmethod
    def do_accept_offer_draw(cls, board: Board) -> bool:
        return False

