#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import Enum

from bitarray import bitarray, frozenbitarray


class MoveParsePhase(Enum):
    START              = 0
    FROM_PIECE_TYPE    = 1
    FROM_FILE          = 2
    FROM_RANK          = 3
    IS_CAPTURE         = 4
    CAPTURE_PIECE_TYPE = 5
    IS_EN_PASSANT      = 6
    TO_FILE            = 7
    TO_RANK            = 8
    IS_PROMOTION       = 9
    PROMOTION_TYPE     = 10
    CHECKNESS          = 11
    MOVE_EVAL          = 12

    def to_bitarray(self):  # Used to determine test coverage
        return bitarray(f'{self.to_int_flag():012b}')

    def to_int_flag(self):  # Used to determine test coverage
        assert self.value > 0
        return 1 << (self.value - 1)
