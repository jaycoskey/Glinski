#!/usr/bin/env python
# by Jay M. Coskey, 2026

from enum import IntFlag

__STR__ = {
            "Claim_NonProgress50": "Claim draw after 50 non-progress moves (100 half-moves)",
            "Claim_Repetition3x": "Claim draw after 3x board position repetition",
            "OfferDraw": "Offer draw",
            "Resign": "Resign",
            "SuggestResignation": "Suggest that the opponent resigns"
            }

class MoveOptionsFlags(IntFlag):
    Claim_NonProgress50 = 1
    Claim_Repetition3x = 2
    OfferDraw = 4
    Resign = 8
    SuggestResignation = 16

    def to_str(self):

        return __STR__[self.name]
