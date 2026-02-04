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
# TODO: but non-core attributes can be updated later.
class Move:
    def __init__(self, fr_npos: Npos, to_npos: Npos, pt_promo: PieceType=None):
        self._fr_npos: int
        self._to_npos: int
        self._pt_promo = None

        self.pt: PieceType = None
        self.is_capture: bool = None
        self.is_check: bool = None
        self.is_checkmate: bool = None
        self.ep_target: Npos = None
        self.pt_capture: PieceType = None

        # Subjective attributes
        self.move_eval = None

    def set_dependent_attributes(self, pt: PieceType, pt_capture: PieceType, ep_target: Npos):
        self.pt: PieceType = pt
        self.is_capture: bool = is_capture
        self.ep_target: Npos = ep_target
        self.pt_capture: PieceType = pt_capture

    def set_computed_attributes(self, is_check, is_checkmate):
        self.is_check: bool = is_check
        self.is_checkmate: bool = is_checkmate

    def set_subjective_attributes(self, move_eval: MoveEval):
        self.move_eval = move_eval

    # ========================================

    @property
    def fr_npos(self):
        return self._fr_npos

    @property
    def to_npos(self):
        return self._to_npos

    @property
    def pt_promo(self):
        return self._pt_promo

    # ========================================

    def __eq__(self, other):
        return (
            self.fr_npos == other.fr_npos
            and self.to_npos == other.to_npos
            and self.pt_promo == other.pt_promo
        )

    # Guaranteed to be uniquely determined by fr_npos, to_npos, and pt_promo:PieceType,
    #   assuming that the values of PieceType remain (distinct) positive integers.
    def __hash__(self):
        SMALL_PRIME = 97
        LARGE_PRIME = 90 + 90 * 97 + 1
        return (self.fr_npos + SMALL_PRIME * self.to_npos
                + LARGE_PRIME * self.pt_promo.value)

    def __str__(self):
        return "{0}{1}{2}{3}".format(
            PieceType.to_symbol(self.pt),
            G.npos_to_alg[self.fr_npos],
            G.npos_to_alg[self.to_npos],
            self.post_str,
        )

    # ========================================

    # TODO: Ensure that other Move instance attributes are copied over.
    def copy(self):
        return Move(self._fr_npos, self._to_npos, self._pt_promo)

    def to_alg(self):
        movetext = self.to_movetext()
        promo = str(self.pt_promo) if self.pt_promo else ''
        check_checkmate = ('#' if self.is_checkmate
                else ('+' if str(self.is_mate) else ''))
        move_eval = str(self.move_eval) if self.move_eval else ''
        suffix = '{1}{2}{3}'.format(promo, check_checkmate, move_eval)
        return movetext + suffix

    def to_movetext(self):
        piece = '' if self.pt == PieceType.Pawn else str(self.pt)
        fr_alg = G.npos_to_pos(self.fr_npos)
        capt = 'x' if self.pt_capt else '',
        to_alg = G.npos_to_pos(self.to_npos)
        movetext = '{1}{2}{3}{4}'.format(piece, fr_alg, capt, to_alg)
        return movetext
