#!/usr/bin/env python # by Jay M. Coskey, 2026

from collections import OrderedDict
import itertools
import re
from typing import Dict, List, Tuple

from src.board import Board
from src.game import Game
from src.geometry import Geometry as G
from src.hex_pos import HexPos
from src.move import Move
from src.move_spec import MoveSpec
from src.move_parse_phase import MoveParsePhase
from src.piece_type import PieceType
from src.player import Player


GameTagPair = Tuple[str, str]
GameTagPairSet = OrderedDict[str, str]
GameSpec = Tuple[GameTagPairSet, List[str]]

# Overview of parsing a PGN file:
#   * TODO: Address comment handling, and handling of turns split across lines.
#   * Split the PGN file into a series of GameSpecs.
#   * Each GameSpec has a series of GameTagPairs, and a list of movetext lines.
#   * Each line has a series of turns, with turn number and "turntext", like so:
#   *     1. g6 Ng9 2. Ni3 e5 3. fxe Qxe5 4. Rg4 Ql3
#   * The turntext is often a pair of moves, but consist of the movetext of a
#     or could repressent two moves plus some trailing text, such the final score.
#   * The parsing of a PGN file involves a local Game object, which tracks the
#     state of the board, to infer the correct piece movement from Game/Board state
#     (e.g., exf). As a last (inefficient) resort, movetext can be disambiguating
#     by searching through a list of all legal moves found from the Game/Board object.
# PGN parsing workflow:
#  get_pgn_lines()
#    -> pgn_lines_to_game_specs()
#      -> move_lines_to_move_texts()
#        -> move_text_to_move_spec()
#          -> get_moves_matching()
class Pgn:
    RE_MOVE_END_SCORE = re.compile(r"^(0-1|1-0|1/2-1/2|draw)$")
    RE_PGN_COMMENT = re.compile(r"{[^}]*}")
    RE_PGN_ELLIPSIS = re.compile(r"\.{3}$")
    RE_PGN_LINE_IS_ATTRIBUTE = re.compile("^\[")
    RE_PGN_LINE_IS_BLANK = re.compile("^\s*")
    RE_PGN_LINE_IS_COMMENT = re.compile("^#")
    RE_PGN_LINE_IS_TURN_NUM = re.compile('^[1-9]')
    RE_PGN_LINE_IS_TURN_NUM = re.compile(r"^(1-9)(0-9)*\.")
    RE_PGN_LINE_NONMOVE     = re.compile('^\s*([#[].*)?')
    RE_PGN_TAG = re.compile(r'^\[(\w+)\s+"([^\]]+)"]$')

    # TODO: Consider returning namedtuple to reduce the risk of error.
    @classmethod
    def fen_to_fen_info(cls, fen: str) -> Tuple:
        fen_parts = fen.split()
        assert(len(fen_parts) == 6)

        #1: Layout
        fen_board_str = fen_parts[0]

        #2: Active color
        cur_player_str = fen_parts[1]
        if cur_player_str == 'b':
            cur_player = Player.Black
        elif cur_player_str == 'w':
            cur_player = Player.White
        else:
            raise ValueError(f'fen_to_fen_info: Unrecognized Player in FEN string')

        #3: Castling availability
        # Note: There is no castling in Glinski's hexagonal chess.
        castling_info = None

        #4: En passant target npos
        ep_tgt_str = fen_parts[3]

        #5: Non-progress halfmove clock
        nonprogress_ctr = int(fen_parts[4])

        #6: Turn/fullmove number
        fullmove_num = int(fen_parts[5])
        halfmove_base = 2 * (fullmove_num - 1)
        halfmove_bump = 1 if cur_player == Player.Black else 0
        halfmove_num = halfmove_base + halfmove_bump

        return (fen_board_str, cur_player, ep_tgt_str,
                nonprogress_ctr, fullmove_num, halfmove_num)

    @classmethod
    def get_layout_dict_empty(cls) -> Dict[Player, Dict[PieceType, List[HexPos]]]:
        PLAYERS = [Player.Black, Player.White]
        PIECE_TYPES = [PieceType.King, PieceType.Queen, PieceType.Rook,
                PieceType.Bishop, PieceType.Knight, PieceType.Pawn]
        layout = {}
        for player in PLAYERS:
            layout[player] = {}
            for pt in PIECE_TYPES:
                layout[player][pt] = []
        return layout

    # Note: This method uses 2 techniques to handle multi-character tokens:
    #   (1) To handle two-digit rank numbers (e.g., 10, 11), the first digit
    #       is cached (into the variable "cached_digit") in one loop iteration,
    #       and the completed rank value (whether 1 or 2 digits) is handled
    #       on the next one.
    #   (2) The various indicators of en-passant capture (ep, ep., e.p.)
    #       are handled when the first letter is detected, using the loop
    #       iteration flag "skip_chars".
    # Note: This method does not process comments or game-end information,
    #       such as score, or indications of how the game ended (agreement
    #       to a draw, or one player resigning).
    @classmethod
    def move_text_to_move_spec(cls, move_str, lang='en') -> MoveSpec:
        move_spec = MoveSpec()

        # TODO: Break up into one set for each Player
        FILE_PROMOTION_SPACES = """a6 b7 c8 d9 e10 f11 g10 h9 i8 k7 l6
                                   a1 b1 c1 d1 e1 f1 g1 h1 i1 k1 l1""".split()
        PROMOTION_PIECES_EN = tuple('QRBN')
        PROMOTION_PIECES_HU = tuple('VBFH')
        PROMOTION_PIECES = (PROMOTION_PIECES_EN
                if lang == 'en' else PROMOTION_PIECES_HU)

        cached_digit = None
        cur_phase = MoveParsePhase.START
        skip_chars = 0
        for k, c in enumerate(move_str):
            if skip_chars > 0:
                skip_chars -= 1
                continue

            if c.isdigit():
                if cached_digit:
                    assert cached_digit == '1'
                    assert c in ['0', '1']  # Ranks don't exceed 11.
                    rank = int(cached_digit + c)
                    cached_digit = None
                    if cur_phase.value < MoveParsePhase.FROM_RANK.value:
                        move_spec.fr_rank = rank
                        cur_phase = MoveParsePhase.FROM_RANK
                        continue
                    if cur_phase.value < MoveParsePhase.TO_RANK.value:
                        move_spec.to_rank = rank
                        cur_phase = MoveParsePhase.TO_RANK
                        continue
                    raise ValueError(f'Rank ({rank}) appears in invalid location')
                if c == '1' and k < len(move_str) - 1:
                    # This digit might be the first digit of a 2-digit rank number.
                    # Prepare to handle it in the next iteration of this character loop.
                    cached_digit = c
                    continue
                # Handle the single-row digit, without caching cache.
                rank = int(c)
                if cur_phase.value < MoveParsePhase.FROM_RANK.value:
                    move_spec.fr_rank = rank
                    cur_phase = MoveParsePhase.FROM_RANK
                elif cur_phase.value < MoveParsePhase.TO_RANK.value:
                    move_spec.to_rank = rank
                    cur_phase = MoveParsePhase.TO_RANK
                continue
            # c is not a digit.
            if cached_digit:
                rank = int(cached_digit)
                cached_digit = None
                if cur_phase.value < MoveParsePhase.FROM_RANK.value:
                    move_spec.fr_rank = rank
                    cur_phase = MoveParsePhase.FROM_RANK
                    # Proceed with this loop iteration, since we still need to handle c.
                elif cur_phase.value < MoveParsePhase.TO_RANK.value:
                    move_spec.to_rank = rank
                    cur_phase = MoveParsePhase.TO_RANK
                    # Proceed with this loop iteration, since we still need to handle c.
                else:
                    raise ValueError(f'Rank ({rank}) appears valid context')
            if c.isupper():
                # UPPER CASE => Represents a PieceType
                if cur_phase == MoveParsePhase.START:
                    move_spec.pt = PieceType.from_symbol(c, lang)
                    cur_phase = MoveParsePhase.FROM_PIECE_TYPE
                    continue
                if cur_phase == MoveParsePhase.IS_CAPTURE:
                    move_spec.capture_pt = PieceType.from_symbol(c, lang)
                    cur_phase = MoveParsePhase.CAPTURE_PIECE_TYPE
                    continue
                if cur_phase == MoveParsePhase.IS_PROMOTION:
                    move_spec.promotion_pt = PieceType.from_symbol(c, lang)
                    cur_phase = MoveParsePhase.PROMOTION_TYPE
                    continue
                if c in PROMOTION_PIECES:
                    # Might indicate a Pawn promotion without a preceding promotion indicator (=).
                    if cur_phase == MoveParsePhase.FROM_RANK:
                        fr_pos = move_spec.fr_file + str(move_spec.fr_rank)
                        if fr_pos in FILE_PROMOTION_SPACES:
                            move_spec.promotion_pt = PieceType.from_symbol(c, lang)
                            cur_phase = MoveParsePhase.PROMOTION_TYPE
                            continue
                    if cur_phase == MoveParsePhase.TO_RANK:
                        to_pos = move_spec.to_file + str(move_spec.to_rank)
                        if to_pos in FILE_PROMOTION_SPACES:
                            move_spec.promotion_pt = PieceType.from_symbol(c, lang)
                            cur_phase = MoveParsePhase.PROMOTION_TYPE
                            continue
                    msg = f'Movetext {move_str}[{k}]=({c}) in invalid context.'
                    raise ValueError(msg + ' Pawn promotion?')
                msg = f'Movetext {move_str}[{k}]=({c}) in invalid context'
                raise ValueError(msg)

            if c.islower():
                if c == 'x':
                    # x => Represents capture
                    assert not move_spec.is_capture  # We can't have multiple of these.
                    move_spec.is_capture = True
                    cur_phase = MoveParsePhase.IS_CAPTURE
                    continue
                # LOWER CASE => Represents a file or 'ep'
                if c not in 'abcdefghikl':
                    raise ValueError(f'In string {move_str}, found an invalid file character: {c}')
                # Check to see if it is the start of an en passant representation
                if c == 'e':
                    if (k < len(move_str) - 1 and move_str[k + 1] == 'p'):
                        # Found en passant
                        move_spec.is_en_passant = True
                        cur_phase = MoveParsePhase.IS_EN_PASSANT
                        if k < len(move_str) - 2 and move_str[k + 2] == '.':
                            skip_chars = 2
                            move_spec.en_passant_str = 'ep.'
                        else:
                            skip_chars = 1
                            move_spec.en_passant_str = 'ep'
                        continue
                    if (k < len(move_str) - 3  # At least 3 chars left in input
                            and move_str[k + 1] == '.'
                            and move_str[k + 1] == 'e'
                            and move_str[k + 1] == '.'):
                        # Found verbose en passant
                        move_spec.is_en_passant = True
                        cur_phase = MoveParsePhase.IS_EN_PASSANT
                        move_spec.en_passant_str = 'e.p.'
                        skip_chars = 3
                        continue
                # Not en passant
                if cur_phase.value < MoveParsePhase.FROM_FILE.value:
                    move_spec.fr_file = c
                    cur_phase = MoveParsePhase.FROM_FILE
                    continue
                if cur_phase.value < MoveParsePhase.TO_FILE.value:
                    move_spec.to_file = c
                    cur_phase = MoveParsePhase.TO_FILE
                    continue
                raise ValueError(f'Invalid state: file symbols ({c}) comes after valid positions')
            if c == '=':
                assert not move_spec.is_promotion  # We can't have multiple of these.
                move_spec.is_promotion = True
                cur_phase = MoveParsePhase.IS_PROMOTION
                continue
            if c in ['+', '#']:
                assert not move_spec.checkness_str  # We can't have multiple of these.
                move_spec.checkness_str = c
                cur_phase = MoveParsePhase.CHECKNESS
                continue
            if c in ['!', '?']:
                if move_spec.move_eval_str:
                    move_spec.move_eval_str += c
                else:
                    move_spec.move_eval_str = c
                continue
            raise ValueError(f'Character with unrecognized role in Move string: {c}')
        assert not cached_digit

        # Final conditional transformation
        if (move_spec.fr_file and move_spec.fr_rank
                and (not move_spec.to_file) and (not move_spec.to_rank)):
            # The eager approach populated the "from" position with file and rank.
            # But it's now apparent that these actually belong to the "to" position.
            move_spec.to_file = move_spec.fr_file
            move_spec.fr_file = None

            move_spec.to_rank = move_spec.fr_rank
            move_spec.fr_rank = None
        return move_spec

    # TODO: Support passing line numbers, so error msgs can point to location in file.
    @classmethod
    def game_spec_to_game(cls, game_spec: GameSpec, lang='en') -> Game:
        game = Game()
        game.set_attributes(game_spec[0])
        game_id = game_spec[0]['GameID'] if 'GameID' in game_spec[0] else '???'

        move_texts = cls.move_lines_to_move_texts(game_spec[1])
        for move_text in move_texts:
            if move_text in ['', '0-1', '1-0', 'draw', 'remi', 'ź-ź', '...']:
                # TODO: Insert info into Game
                continue
            move_spec = cls.move_text_to_move_spec(move_text, lang)
            moves = game.board.get_moves_matching(move_spec, move_text)
            if len(moves) != 1:
                print(f'Game tag pairs={", ".join(f"({k}=>{v})" for k,v in game_spec[0].items())}')
                print(f'Game moves={move_texts}')
                game.board.print()
                ep_str = f'{game.board.ep_target if game.board.ep_target else "None"}'
                print(f'Halfmove_count={game.board.halfmove_count}, '
                        + f'move_text={move_text} '
                        + f'(ep_target={ep_str}, lang={lang})'
                        )
                if len(moves) == 0:
                    print(f'No moves available')
                elif len(moves) > 1:
                    print(f'Multiple moves available: {moves}')
                assert len(moves) == 1
            move = moves[0]
            game.board.move_make(move)
        return game

    @classmethod
    def get_game_tag_pair(cls, line: str, line_num: int) -> GameTagPair:
        tag_pair_re = re.compile('\[(\w+)\s+"([^"]+)"\]$')
        match = re.match(tag_pair_re, line)
        if match:
            return (match.group(1), match.group(2))
        else:
            raise ValueError(f'Unexpected tag pair syntax at line {line_num}: {line}')

    @classmethod
    def get_pgn_lines(cls, fname: str) -> List[str]:
        with open(fname, 'r') as f:
            return [line.strip() for line in f.readlines()]

    @classmethod
    def is_line_blank(cls, line) -> bool:
        blank_re = re.compile('^\s*$')
        match = re.match(blank_re, line)
        return bool(match)

    @classmethod
    def is_line_game_tag_pair(cls, line) -> bool:
        return line[0] == '['

    @classmethod
    def is_line_move_text(cls, line) -> bool:
        return line[0].isdigit()

    # Note: Currently, each turn is expected to be contained within a single line.
    def move_lines_to_turn_texts(lines: List[str], lang='en') -> List[List[Move]]:
        raise NotImplementedError('Pgn.move_lines_to_turn_texts()')

    # Note: Currently, each turn is expected to be contained within a single line.
    def move_lines_to_move_texts(lines: List[str], lang='en') -> List[str]:
        # TODO: Remove comments
        # TODO: Carry over file line_num from the calling context
        # TODO: Handle post-move text, such as "draw" or a score, etc.
        expected_turn_num = 1
        turn_texts = []

        COMMENT_RE = re.compile(r"\{[^}].*\}")
        TURN_NUMS_RE = re.compile(r"(\d+)\.")
        for line_num, line in enumerate(lines):
            line = re.sub(COMMENT_RE, "", line)
            turn_matches = list(re.finditer(TURN_NUMS_RE, line))
            jmc_turn_num_spans = [turn_match.span() for turn_match in turn_matches]
            turn_num_texts = [
                    line[int(turn.span()[0]): int(turn.span()[1])-1]
                    for turn in turn_matches
                    ]
            turn_nums = [int(turn_num_text) for turn_num_text in turn_num_texts]

            # Verify that the turns are appropriately numbered
            for k in range(len(turn_nums)):
                assert turn_nums[k] == expected_turn_num
                expected_turn_num += 1

            # From the regexp identifying the spans for the turn numbers,
            # we can identify the text between/after the turn numbers.
            # Chop the line into move text chunks.
            # Each chunk should have 1 or 2 moves, & possibly the final score.
            line_turn_texts = []
            for k in range(len(turn_matches)):
                a = int(turn_matches[k].span()[1])
                b = int(turn_matches[k+1].span()[0]) if k < len(turn_matches) - 1 else len(line)
                line_turn_texts.append(line[a: b].strip())
            if len(turn_num_texts) != len(line_turn_texts):
                print(f'line={line}: Counts of turn #s ({turn_num_texts}~{len(turn_num_texts)} and line turn texts ({line_turn_texts}~{len(line_turn_texts)}) do not match')
            assert len(turn_num_texts) == len(line_turn_texts)
            turn_texts.extend(line_turn_texts)
        move_texts = [move_text for turn_text in turn_texts for move_text in turn_text.split(' ')]
        return move_texts

    @classmethod
    def move_text_to_move(cls, board: Board, move_text: str):
        move_spec = cls.move_text_to_move_spec(move_text)
        moves = board.get_moves_matching(move_spec, move_text)
        assert len(moves) == 1
        return moves[0]

    # PGN files specify games. Each game has tags which specify attributes of the game,
    # and text that specifies the moves of the game.
    #
    # TODO: Remove PGN comments that span multiple lines.
    @classmethod
    def pgn_lines_to_game_specs(cls, lines: List[str], tag_filter: Dict[str, str]=None) -> List[GameSpec]:
        game_specs = []
        game_tags = OrderedDict[str, str]()
        move_text = []
        is_in_moves  = False
        is_in_tags   = False
        is_rejecting = False

        for line_num, line in enumerate(lines, start=1):
            if cls.is_line_blank(line):
                continue
            if cls.is_line_move_text(line):
                if is_in_tags:
                    is_in_tags = False
                is_in_moves = True
                if is_rejecting:
                    continue
                move_text.append(line)
                continue
            if cls.is_line_game_tag_pair(line):
                if is_in_moves:
                    # Before we starting new game, wrap up the current one
                    if is_rejecting:
                        is_rejecting = False
                    else:
                        tag_str = ';'.join([f'{k}=>{v}' for k,v in game_tags.items()])
                        do_record_game_spec = True
                        if tag_filter:
                            for k, v in tag_filter.items():
                                if k not in game_tags or game_tags[k] != v:
                                    do_record_game_spec = False
                                    break
                        if do_record_game_spec:
                            game_spec = (game_tags, move_text)
                            game_specs.append(game_spec)
                    # And start over
                    game_tags = OrderedDict[str, str]()
                    move_text = []
                is_in_tags = True
                is_in_moves = False
                if is_rejecting:
                    continue
                # Now we're ready for the current game's tag pairs.
                game_tag_pair = cls.get_game_tag_pair(line, line_num)
                key = game_tag_pair[0]
                val = game_tag_pair[1]
                if tag_filter and key in tag_filter and val != tag_filter[key]:
                    is_rejecting = True
                    continue
                game_tags[game_tag_pair[0]] = game_tag_pair[1]

        # Handle any accumulated but unprocesed state
        if len(move_text) > 0 and not is_rejecting:
            do_record_game_spec = True
            if tag_filter:
                for k, v in tag_filter.items():
                    if k not in game_tags or game_tags[k] != v:
                        do_record_game_spec = False
                        break
            if do_record_game_spec:
                game_spec = (game_tags, move_text)
                game_specs.append(game_spec)
        return game_specs

    @classmethod
    def uci_to_move(cls, move_str, lang='en') -> Move:
        raise NotImplementedError('Pgn.uci_to_move')

