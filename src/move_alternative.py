#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import Enum


class MoveAlternative(Enum):
    ClaimNonProgress50 = 0
    ClaimRepetition3x = 1
    OfferDraw = 2
    Resign = 3

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        strs = [
            'Claim draw after 50 non-progress moves (100 half-moves)',
            'Claim draw after 3x board position repetition',
            'Offer draw to opponent',
            'Resign'
            ]
        return strs[self.value]

