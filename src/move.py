#!/usr/bin/env python
# by Jay M. Coskey, 2026

import re
import sys

from src.geometry import Geometry as G
from src.move_eval import MoveEval
from src.move_regexp import MoveRegexp
from src.piece_type import PieceType

Npos = int


# TODO: Integrate actions that can take besides Moves. (See class MoveOptionFlags.)
# TODO: Moves are instantiated with only 3 arguments (from, to, promotion type),
# TODO: but non-core attributes (e.g., move evaluation) can be updated later.
class Move:
    def __init__(self, fr_npos: Npos, to_npos: Npos, promo_pt: PieceType=None):
        self._fr_npos: int = fr_npos
        self._to_npos: int = to_npos
        self._promo_pt = None

        self.pt: PieceType = None
        self.is_check: bool = None
        self.is_checkmate: bool = None
        self.ep_target: Npos = None
        self.capture_pt: PieceType = None

        # Subjective attributes
        self.move_eval = None

    def set_dependent_attributes(self, pt: PieceType, capture_pt: PieceType, ep_target: Npos):
        self.pt: PieceType = pt
        self.ep_target: Npos = ep_target
        self.capture_pt: PieceType = capture_pt

    def set_computed_attributes(self, is_check, is_checkmate):
        self.is_check: bool = is_check
        self.is_checkmate: bool = is_checkmate

    def set_subjective_attributes(self, move_eval: MoveEval):
        self.move_eval = move_eval

    # ========================================
    # Properties

    @property
    def fr_npos(self):
        return self._fr_npos

    @property
    def to_npos(self):
        return self._to_npos

    @property
    def promo_pt(self):
        return self._promo_pt

    # ========================================

    def __eq__(self, other):
        return (
            self.fr_npos == other.fr_npos
            and self.to_npos == other.to_npos
            and self.promo_pt == other.promo_pt
        )

    # Guaranteed to be uniquely determined by fr_npos, to_npos, and promo_pt:PieceType,
    #   assuming that the values of PieceType remain (distinct) positive integers.
    def __hash__(self):
        SMALL_PRIME = 97
        LARGE_PRIME = 90 + 90 * 97 + 1
        return (self.fr_npos + SMALL_PRIME * self.to_npos
                + LARGE_PRIME * self.promo_pt.value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{0}{1}{2}{3}'.format(
            PieceType.to_symbol(self.pt) if self.pt else '-',
            G.npos_to_alg(self.fr_npos) if self.fr_npos else '-',
            G.npos_to_alg(self.to_npos) if self.to_npos else '-'
            '=' + PieceType.to_symbol(self.promo_pt) if self.promo_pt else ''
        )

    # ========================================

    # TODO: Ensure that other Move instance attributes are copied over.
    def copy(self):
        return Move(self._fr_npos, self._to_npos, self._promo_pt)

    def is_progress(self):
        return self.capture_pt or self.pt == PieceType.Pawn

    def to_alg(self):
        movetext = self.to_movetext()
        promo = str(self.promo_pt) if self.promo_pt else ''
        check_checkmate = ('#' if self.is_checkmate
                else ('+' if str(self.is_mate) else ''))
        move_eval = str(self.move_eval) if self.move_eval else ''
        suffix = '{1}{2}{3}'.format(promo, check_checkmate, move_eval)
        return movetext + suffix

    def to_movetext(self):
        piece = '' if self.pt == PieceType.Pawn else str(self.pt)
        fr_alg = G.npos_to_pos(self.fr_npos)
        capt = 'x' if self.capture_pt else '',
        to_alg = G.npos_to_pos(self.to_npos)
        movetext = '{1}{2}{3}{4}'.format(piece, fr_alg, capt, to_alg)
        return movetext
