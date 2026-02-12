#!/usr/bin/env python
# by Jay M. Coskey, 2026

from src.move_info import MoveInfo
from src.move_parse_phase import MoveParsePhase
from src.piece_type import PieceType


class Pgn:
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
    def alg_to_moveinfo(cls, move_str, lang='en') -> MoveInfo:
        move_info = MoveInfo()

        # TODO: Break up into one set for each Player
        FILE_PROMOTION_SPACES = """a6 b7 c8 d9 e10 f11 g10 h9 i8 k7 l6
                                   a1 b1 c1 d1 e1 f1 g1 h1 i1 k1 l1""".split()
        PROMOTION_PIECES_EN = tuple('QRBN')
        PROMOTION_PIECES_HU = tuple('VBFH')
        PROMOTION_PIECES = PROMOTION_PIECES_EN if lang == 'en' else PROMOTION_PIECES_HU

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
                        move_info.fr_rank = rank
                        cur_phase = MoveParsePhase.FROM_RANK
                        continue
                    if cur_phase.value < MoveParsePhase.TO_RANK.value:
                        move_info.to_rank = rank
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
                    move_info.fr_rank = rank
                    cur_phase = MoveParsePhase.FROM_RANK
                elif cur_phase.value < MoveParsePhase.TO_RANK.value:
                    move_info.to_rank = rank
                    cur_phase = MoveParsePhase.TO_RANK
                continue
            # c is not a digit.
            if cached_digit:
                rank = int(cached_digit)
                cached_digit = None
                if cur_phase.value < MoveParsePhase.FROM_RANK.value:
                    move_info.fr_rank = rank
                    cur_phase = MoveParsePhase.FROM_RANK
                    # Proceed with this loop iteration, since we still need to handle c.
                elif cur_phase.value < MoveParsePhase.TO_RANK.value:
                    move_info.to_rank = rank
                    cur_phase = MoveParsePhase.TO_RANK
                    # Proceed with this loop iteration, since we still need to handle c.
                else:
                    raise ValueError(f'Rank ({rank}) appears valid context')
            if c.isupper():
                # UPPER CASE => Represents a PieceType
                if cur_phase == MoveParsePhase.START:
                    move_info.fr_pt = PieceType.from_symbol(c, lang)
                    cur_phase = MoveParsePhase.FROM_PIECE_TYPE
                    continue
                if cur_phase == MoveParsePhase.IS_CAPTURE:
                    move_info.capture_pt = PieceType.from_symbol(c, lang)
                    cur_phase = MoveParsePhase.CAPTURE_PIECE_TYPE
                    continue
                if cur_phase == MoveParsePhase.IS_PROMOTION:
                    move_info.promotion_pt = PieceType.from_symbol(c, lang)
                    cur_phase = MoveParsePhase.PROMOTION_TYPE
                    continue
                if c in PROMOTION_PIECES:
                    # Might indicate a Pawn promotion without a preceding promotion indicator (=).
                    if cur_phase == MoveParsePhase.FROM_RANK:
                        fr_pos = move_info.fr_file + str(move_info.fr_rank)
                        if fr_pos in FILE_PROMOTION_SPACES:
                            move_info.promotion_pt = PieceType.from_symbol(c, lang)
                            cur_phase = MoveParsePhase.PROMOTION_TYPE
                            continue
                    if cur_phase == MoveParsePhase.TO_RANK:
                        to_pos = move_info.to_file + str(move_info.to_rank)
                        if to_pos in FILE_PROMOTION_SPACES:
                            move_info.promotion_pt = PieceType.from_symbol(c, lang)
                            cur_phase = MoveParsePhase.PROMOTION_TYPE
                            continue
                    msg = f'Movetext {move_str}[{k}]=({c}) in invalid context.'
                    raise ValueError(msg + ' Pawn promotion?')
                msg = f'Movetext {move_str}[{k}]=({c}) in invalid context'
                raise ValueError(msg)

            if c.islower():
                if c == 'x':
                    # x => Represents capture
                    assert not move_info.is_capture  # We can't have multiple of these.
                    move_info.is_capture = True
                    cur_phase = MoveParsePhase.IS_CAPTURE
                    continue
                # LOWER CASE => Represents a file or 'ep'
                if c not in 'abcdefghikl':
                    raise ValueError(f'In string {move_str}, found an invalid file character: {c}')
                if c == 'e':
                    if (k < len(move_str) - 1 and move_str[k + 1] == 'p'):
                        # Found en passant
                        move_info.is_en_passant = True
                        cur_phase = MoveParsePhase.IS_EN_PASSANT
                        if k < len(move_str) - 2 and move_str[k + 2] == '.':
                            skip_chars = 2
                            move_info.en_passant_str = 'ep.'
                        else:
                            skip_chars = 1
                            move_info.en_passant_str = 'ep'
                        continue
                    if (k < len(move_str) - 3  # At least 3 chars left in input
                            and move_str[k + 1] == '.'
                            and move_str[k + 1] == 'e'
                            and move_str[k + 1] == '.'):
                        # Found verbose en passant
                        move_info.is_en_passant = True
                        cur_phase = MoveParsePhase.IS_EN_PASSANT
                        move_info.en_passant_str = 'e.p.'
                        skip_chars = 3
                        continue
                # Not en passant
                if cur_phase.value < MoveParsePhase.FROM_FILE.value:
                    move_info.fr_file = c
                    cur_phase = MoveParsePhase.FROM_FILE
                    continue
                if cur_phase.value < MoveParsePhase.TO_FILE.value:
                    move_info.to_file = c
                    cur_phase = MoveParsePhase.TO_FILE
                    continue
                raise ValueError(f'Invalid state: file symbols ({c}) comes after valid positions')
            if c == '=':
                assert not move_info.is_promotion  # We can't have multiple of these.
                move_info.is_promotion = True
                cur_phase = MoveParsePhase.IS_PROMOTION
                continue
            if c in ['+', '#']:
                assert not move_info.checkness_str  # We can't have multiple of these.
                move_info.checkness_str = c
                cur_phase = MoveParsePhase.CHECKNESS
                continue
            if c in ['!', '?']:
                if move_info.move_eval_str:
                    move_info.move_eval_str += c
                else:
                    move_info.move_eval_str = c
                continue
            raise ValueError(f'Character with unrecognized role in Move string: {c}')
        assert not cached_digit

        # Final conditional transformation
        if (move_info.fr_file and move_info.fr_rank
                and (not move_info.to_file) and (not move_info.to_rank)):
            # The eager approach populated the "from" position with file and rank.
            # But it's now apparent that these actually belong to the "to" position.
            move_info.to_file = move_info.fr_file
            move_info.fr_file = None

            move_info.to_rank = move_info.fr_rank
            move_info.fr_rank = None
        return move_info
