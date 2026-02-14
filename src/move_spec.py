#!/usr/bin/env python
# by Jay M. Coskey, 2026

from bitarray import bitarray, frozenbitarray

from src.move_parse_phase import MoveParsePhase
from src.piece_type import PieceType


# TODO: Consider changing name to MoveSpec.
#
# In the move Qc3xBf9#!
#   Q ~ fr_pt
#   c = fr_file
#   3 ~ fr_rank
#   x ~ is_capture
#   B ~ capture_pt
#   f ~ to_file
#   9 ~ to_rank
#   # ~ checkness
#   ! ~ move_eval
# This example does not illustrate Pawn promotion (=) or en passant (ep, e.p., etc.).
class MoveSpec:
    fr_pt: PieceType        = None  # 1
    fr_file: str            = ''    # 2
    fr_rank: int            = None  # 3

    is_capture: bool        = None  # 4
    capture_pt: PieceType   = None  # 5
    is_en_passant: bool     = None  # 6
    en_passant_str: str     = None

    to_file: str            = ''    # 7
    to_rank: int            = None  # 8

    is_promotion: bool      = None  # 9
    promotion_pt: PieceType = None  # 10
    checkness_str: str      = ''    # 11
    move_eval_str: str      = ''    # 12

    def __str__(self):
        return self.to_str(lang='en')

    # Used to determine test coverage
    def to_move_sig(self) -> frozenbitarray:
        sig = bitarray(12)
        if self.fr_pt:
            sig |= MoveParsePhase.FROM_PIECE_TYPE.to_bitarray()
        if self.fr_file:
            sig |= MoveParsePhase.FROM_FILE.to_bitarray()
        if self.fr_rank:
            sig |= MoveParsePhase.FROM_RANK.to_bitarray()

        if self.is_capture:
            sig |= MoveParsePhase.IS_CAPTURE.to_bitarray()
        if self.capture_pt:
            sig |= MoveParsePhase.CAPTURE_PIECE_TYPE.to_bitarray()
        if self.is_en_passant:
            sig |= MoveParsePhase.IS_EN_PASSANT.to_bitarray()

        if self.to_file:
            sig |= MoveParsePhase.TO_FILE.to_bitarray()
        if self.to_rank:
            sig |= MoveParsePhase.TO_RANK.to_bitarray()

        if self.is_promotion:
            sig |= MoveParsePhase.IS_PROMOTION.to_bitarray()
        if self.promotion_pt:
            sig |= MoveParsePhase.PROMOTION_TYPE.to_bitarray()
        if self.checkness_str:
            sig |= MoveParsePhase.CHECKNESS.to_bitarray()
        if self.move_eval_str:
            sig |= MoveParsePhase.MOVE_EVAL.to_bitarray()
        return frozenbitarray(sig)

    def to_str(self, lang='en'):
        return '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}'.format(

            self.fr_pt.to_symbol(lang) if self.fr_pt else '',
            self.fr_file if self.fr_file else '',
            self.fr_rank if self.fr_rank else '',
            'x' if self.is_capture else '',
            self.capture_pt.to_symbol(lang) if self.capture_pt else '',

            self.to_file,
            self.to_rank if self.to_rank else '',
            self.en_passant_str if self.is_en_passant else '',
            '=' if self.is_promotion else '',
            self.promotion_pt.to_symbol(lang) if self.promotion_pt else '',

            self.checkness_str,
            self.move_eval_str)
