#!/usr/bin/env python
# by Jay M. Coskey, 2026

import re

from src.bitboard import *
from src.hex_pos import HexPos
from src.hex_vec import HexVec

from src.util import static_init


@static_init
class Geometry:
    @classmethod
    def static_init(cls):
        #
        # Preliminary constants that use geometric layouts
        # in their definitions
        #
        BOARD_SPACE_NAMES = """
                          A6  A5  A4  A3  A2  A1
                        B7  B6  B5  B4  B3  B2  B1
                      C8  C7  C6  C5  C4  C3  C2  C1
                    D9  D8  D7  D6  D5  D4  D3  D2  D1
                  E10 E9  E8  E7  E6  E5  E4  E3  E2  E1
                F11 F10 F9  F8  F7  F6  F5  F4  F3  F2  F1
                  G10 G9  G8  G7  G6  G5  G4  G3  G2  G1
                    H9  H8  H7  H6  H5  H4  H3  H2  H1
                      I8  I7  I6  I5  I4  I3  I2  I1
                        K7  K6  K5  K4  K3  K2  K1
                          L6  L5  L4  L3  L2  L1
        """.split()
        setattr(cls, "BOARD_SPACE_NAMES", BOARD_SPACE_NAMES)

        COORD_HEX0 = list(map(int, """
                         -5  -5  -5  -5  -5  -5
                       -4  -4  -4  -4  -4  -4  -4
                     -3  -3  -3  -3  -3  -3  -3  -3
                   -2  -2  -2  -2  -2  -2  -2  -2  -2
                 -1  -1  -1  -1  -1  -1  -1  -1  -1  -1
                0   0   0   0   0   0   0   0   0   0   0
                  1   1   1   1   1   1   1   1   1   1
                    2   2   2   2   2   2   2   2   2
                      3   3   3   3   3   3   3   3
                        4   4   4   4   4   4   4
                          5   5   5   5   5   5
            """.split()))
        setattr(cls, "COORD_HEX0", COORD_HEX0)

        COORD_HEX1 = list(map(int, """
                          0  -1  -2  -3  -4  -5
                        1   0  -1  -2  -3  -4  -5
                      2   1   0  -1  -2  -3  -4  -5
                    3   2   1   0  -1  -2  -3  -4  -5
                  4   3   2   1   0  -1  -2  -3  -4  -5
                5   4   3   2   1   0  -1  -2  -3  -4  -5
                  5   4   3   2   1   0  -1  -2  -3  -4
                    5   4   3   2   1   0  -1  -2  -3
                      5   4   3   2   1   0  -1  -2
                        5   4   3   2   1   0  -1
                          5   4   3   2   1   0
            """.split()))
        setattr(cls, "COORD_HEX1", COORD_HEX1)

        #
        # DEFINE SPACES_COUNT
        #
        SPACES_COUNT = 91
        setattr(cls, "SPACES_COUNT", SPACES_COUNT)

        FILE_CHARS = list("abcdefghikl")
        FILE_CHAR_TO_HEX0 = {
            # GREP Coordinates choice
            letter: k - 5 for k, letter in enumerate(FILE_CHARS)
            }
        setattr(cls, "FILE_CHAR_TO_HEX0", FILE_CHAR_TO_HEX0)

        def alg_to_pos(alg: str):
            pos_re = re.compile(r"([a-lA-L])(10|11|[1-9])")
            result = pos_re.search(alg)
            if not result:
                raise ValueError(f"Regular expression failed on <<{alg}>>")
            hex0 = FILE_CHAR_TO_HEX0[result.group(1).lower()]
            rank = int(result.group(2))
            hex1 = rank - 6 + max(0, hex0)
            return HexPos(hex0, hex1)

        # Define Board Spaces
        #     A6 ... A1 ...... F11 ... F1 ...... L6 ... L1
        #
        A1 = alg_to_pos('a1'); A2 = alg_to_pos('a2'); A3 = alg_to_pos('a3');
        A4 = alg_to_pos('a4'); A5 = alg_to_pos('a5'); A6 = alg_to_pos('a6');

        B1 = alg_to_pos('b1'); B2 = alg_to_pos('a5'); B3 = alg_to_pos('b3');
        B4 = alg_to_pos('a4'); B5 = alg_to_pos('a5'); B6 = alg_to_pos('b6');
        B7 = alg_to_pos('a7');

        C1 = alg_to_pos('c1'); C2 = alg_to_pos('c5'); C3 = alg_to_pos('c3');
        C4 = alg_to_pos('c4'); C5 = alg_to_pos('c5'); C6 = alg_to_pos('c6');
        C7 = alg_to_pos('c7'); C7 = alg_to_pos('c7');

        D1 = alg_to_pos('d1'); D2 = alg_to_pos('d5'); D3 = alg_to_pos('d3');
        D4 = alg_to_pos('d4'); D5 = alg_to_pos('d5'); D6 = alg_to_pos('d6');
        D7 = alg_to_pos('d7'); D7 = alg_to_pos('d7'); D8 = alg_to_pos('d8');

        E1 = alg_to_pos('e1'); E2 = alg_to_pos('e5'); E3 = alg_to_pos('e3');
        E4 = alg_to_pos('e4'); E5 = alg_to_pos('e5'); E6 = alg_to_pos('e6');
        E7 = alg_to_pos('e7'); E7 = alg_to_pos('e7'); E8 = alg_to_pos('e8');
        E9 = alg_to_pos('e9');

        F1 = alg_to_pos('f1'); F2 = alg_to_pos('f5'); F3 = alg_to_pos('f3');
        F4 = alg_to_pos('f4'); F5 = alg_to_pos('f5'); F6 = alg_to_pos('f6');
        F7 = alg_to_pos('f7'); F7 = alg_to_pos('f7'); F8 = alg_to_pos('f8');
        F9 = alg_to_pos('f9'); F10 = alg_to_pos('f10');

        G1 = alg_to_pos('g1'); G2 = alg_to_pos('g5'); G3 = alg_to_pos('g3');
        G4 = alg_to_pos('g4'); G5 = alg_to_pos('g5'); G6 = alg_to_pos('g6');
        G7 = alg_to_pos('g7'); G7 = alg_to_pos('g7'); G8 = alg_to_pos('g8');
        G9 = alg_to_pos('g9');

        H1 = alg_to_pos('h1'); H2 = alg_to_pos('h5'); H3 = alg_to_pos('h3');
        H4 = alg_to_pos('h4'); H5 = alg_to_pos('h5'); H6 = alg_to_pos('h6');
        H7 = alg_to_pos('h7'); H8 = alg_to_pos('h8'); H9 = alg_to_pos('h9');

        I1 = alg_to_pos('h1'); I2 = alg_to_pos('h5'); I3 = alg_to_pos('h3');
        I4 = alg_to_pos('h4'); I5 = alg_to_pos('h5'); I6 = alg_to_pos('h6');
        I7 = alg_to_pos('h7'); I8 = alg_to_pos('h8');

        K1 = alg_to_pos('k1'); K2 = alg_to_pos('k5'); K3 = alg_to_pos('k3');
        K4 = alg_to_pos('k4'); K5 = alg_to_pos('k5'); K6 = alg_to_pos('k6');
        K7 = alg_to_pos('k7');

        L1 = alg_to_pos('l1'); L2 = alg_to_pos('l5'); L3 = alg_to_pos('l3');
        L4 = alg_to_pos('l4'); L5 = alg_to_pos('l5'); L6 = alg_to_pos('l6');

        for k, alg in enumerate(BOARD_SPACE_NAMES):
            setattr(cls, alg, alg_to_pos(alg))

        ZERO = HexVec(0, 0)
        setattr(cls, "ZERO", ZERO)

        #
        # Define all 12 directions
        #
        VEC0 = HexVec(0, 1)
        VEC1 = HexVec(1, 2)
        VEC2 = HexVec(1, 1)
        VEC3 = HexVec(2, 1)
        VEC4 = HexVec(1, 0)
        VEC5 = HexVec(1, -1)

        VEC6 = HexVec(0, -1)
        VEC7 = HexVec(-1, -2)
        VEC8 = HexVec(-1, -1)
        VEC9 = HexVec(-2, -1)
        VEC10 = HexVec(-1, 0)
        VEC11 = HexVec(-1, 1)

        VECS_CLOCK = [
            (0, 1), (1, 2), (1, 1),       # VEC0 .. VEC2
            (2, 1), (1, 0), (1, -1),      # VEC3 .. VEC5
            (0, -1), (-1, -2), (-1, -1),  # VEC6 .. VEC8
            (-2, -1), (-1, 0), (-1, 1)    # VEC9 .. VEC11
            ]
        for hour, coords in enumerate(VECS_CLOCK):
            setattr(cls, "VEC" + str(hour + 1), HexVec(*coords))

        #
        # Define slider directions
        #
        VECS_ORTHO = [VEC0, VEC2, VEC4, VEC6, VEC8, VEC10]
        setattr(cls, "VECS_ORTHO", VECS_ORTHO)

        VECS_DIAG = [VEC1, VEC3, VEC5, VEC7, VEC9, VEC11]
        setattr(cls, "VECS_DIAG", VECS_DIAG)

        VECS_12 = VECS_ORTHO + VECS_DIAG
        setattr(cls, "VECS_12", VECS_12)

        #
        # Define Knight movement directions
        #
        VECS_KNIGHT = [
            2 * VEC0 + VEC2,
            2 * VEC0 + VEC10,
            2 * VEC2 + VEC0,
            2 * VEC2 + VEC4,
            2 * VEC4 + VEC2,
            2 * VEC4 + VEC6,
            2 * VEC6 + VEC4,
            2 * VEC6 + VEC8,
            2 * VEC8 + VEC6,
            2 * VEC8 + VEC10,
            2 * VEC10 + VEC0,
            2 * VEC10 + VEC8,
        ]
        setattr(cls, "VECS_KNIGHT", VECS_KNIGHT)

        #
        # Define Pawn movement directions
        #
        VECS_PAWN_BLACK_ADV = [VEC6]
        VECS_PAWN_BLACK_CAPT = [VEC4, VEC8]
        VECS_PAWN_BLACK_HOP = [2 * VEC6]

        VECS_PAWN_WHITE_ADV = [VEC0]
        VECS_PAWN_WHITE_CAPT = [VEC2, VEC10]
        VECS_PAWN_WHITE_HOP = [2 * VEC0]

        setattr(cls, "VECS_PAWN_BLACK_ADV", VECS_PAWN_WHITE_ADV)
        setattr(cls, "VECS_PAWN_BLACK_CAPT", VECS_PAWN_WHITE_CAPT)
        setattr(cls, "VECS_PAWN_BLACK_HOP", VECS_PAWN_WHITE_HOP)

        setattr(cls, "VECS_PAWN_WHITE_ADV", VECS_PAWN_WHITE_ADV)
        setattr(cls, "VECS_PAWN_WHITE_CAPT", VECS_PAWN_WHITE_CAPT)
        setattr(cls, "VECS_PAWN_WHITE_HOP", VECS_PAWN_WHITE_HOP)

    @classmethod
    def alg_to_pos(cls, alg: str):
        pos_re = re.compile(r"([a-lA-L])(10|11|[1-9])")
        result = pos_re.search(alg)
        if not result:
            raise ValueError(f"Regular expression failed on <<{alg}>>")
        hex0 = cls.FILE_CHAR_TO_HEX0[result.group(1).lower()]
        rank = int(result.group(2))
        hex1 = rank - 6 + max(0, hex0)
        return HexPos(hex0, hex1)

    @classmethod
    def npos_to_alg(cls, n: int) -> str:
        return cls.BOARD_SPACE_NAMES[n].lower()

    @classmethod
    def npos_to_pos(cls, n: int) -> str:
        return HexPos(cls.COORD_HEX0, cls.COORD_HEX1)
