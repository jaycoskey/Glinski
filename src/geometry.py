#!/usr/bin/env python
# by Jay M. Coskey, 2026

import re
from typing import List

from src.bitboard import *
from src.board_color import BoardColor
from src.hex_pos import HexPos
from src.hex_vec import HexVec
from src.piece_type import PieceType
from src.player import Player

from src.util import static_init

Npos = int


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

        RANK = list(map(int, """
                      6   5   4   3   2   1
                    7   6   5   4   3   2   1
                  8   7   6   5   4   3   2   1
                9   8   7   6   5   4   3   2   1
             10   9   8   7   6   5   4   3   2   1
           11  10   9   8   7   6   5   4   3   2   1
             10   9   8   7   6   5   4   3   2   1
                9   8   7   6   5   4   3   2   1
                  8   7   6   5   4   3   2   1
                    7   6   5   4   3   2   1
                      6   5   4   3   2   1
            """.split()))
        setattr(cls, "RANK", RANK)

        #
        # Define SPACE_COUNT
        #
        SPACE_COUNT = 91
        setattr(cls, "SPACE_COUNT", SPACE_COUNT)

        COORDS_TO_NPOS = {
                (COORD_HEX0[npos], COORD_HEX1[npos]): npos
                for npos in range(SPACE_COUNT) }
        setattr(cls, "COORDS_TO_NPOS", COORDS_TO_NPOS)

        FILE_CHARS = list("abcdefghikl")
        setattr(cls, "FILE_CHARS", FILE_CHARS)
        FILE_CHAR_TO_HEX0 = {
            # GREP Choice of coordinates
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

        # ========================================

        # Define Board Spaces
        #     A6 ... A1 ...... F11 ... F1 ...... L6 ... L1
        #
        A1 = alg_to_pos('a1'); A2 = alg_to_pos('a2'); A3 = alg_to_pos('a3');
        A4 = alg_to_pos('a4'); A5 = alg_to_pos('a5'); A6 = alg_to_pos('a6');

        B1 = alg_to_pos('b1'); B2 = alg_to_pos('b2'); B3 = alg_to_pos('b3');
        B4 = alg_to_pos('b4'); B5 = alg_to_pos('b5'); B6 = alg_to_pos('b6');
        B7 = alg_to_pos('b7');

        C1 = alg_to_pos('c1'); C2 = alg_to_pos('c2'); C3 = alg_to_pos('c3');
        C4 = alg_to_pos('c4'); C5 = alg_to_pos('c5'); C6 = alg_to_pos('c6');
        C7 = alg_to_pos('c7'); C8 = alg_to_pos('c8');

        D1 = alg_to_pos('d1'); D2 = alg_to_pos('d2'); D3 = alg_to_pos('d3');
        D4 = alg_to_pos('d4'); D5 = alg_to_pos('d5'); D6 = alg_to_pos('d6');
        D7 = alg_to_pos('d7'); D8 = alg_to_pos('d8'); D9 = alg_to_pos('d9');

        E1 = alg_to_pos('e1'); E2 = alg_to_pos('e2'); E3 = alg_to_pos('e3');
        E4 = alg_to_pos('e4'); E5 = alg_to_pos('e5'); E6 = alg_to_pos('e6');
        E7 = alg_to_pos('e7'); E8 = alg_to_pos('e8'); E9 = alg_to_pos('e9');
        E10 = alg_to_pos('e10');

        F1 = alg_to_pos('f1'); F2 = alg_to_pos('f2'); F3 = alg_to_pos('f3');
        F4 = alg_to_pos('f4'); F5 = alg_to_pos('f5'); F6 = alg_to_pos('f6');
        F7 = alg_to_pos('f7'); F8 = alg_to_pos('f8'); F9 = alg_to_pos('f9');
        F10 = alg_to_pos('f10'); F11 = alg_to_pos('f11');

        G1 = alg_to_pos('g1'); G2 = alg_to_pos('g2'); G3 = alg_to_pos('g3');
        G4 = alg_to_pos('g4'); G5 = alg_to_pos('g5'); G6 = alg_to_pos('g6');
        G7 = alg_to_pos('g7'); G8 = alg_to_pos('g8'); G9 = alg_to_pos('g9');
        G10 = alg_to_pos('g10');

        H1 = alg_to_pos('h1'); H2 = alg_to_pos('h2'); H3 = alg_to_pos('h3');
        H4 = alg_to_pos('h4'); H5 = alg_to_pos('h5'); H6 = alg_to_pos('h6');
        H7 = alg_to_pos('h7'); H8 = alg_to_pos('h8'); H9 = alg_to_pos('h9');

        I1 = alg_to_pos('i1'); I2 = alg_to_pos('i2'); I3 = alg_to_pos('i3');
        I4 = alg_to_pos('i4'); I5 = alg_to_pos('i5'); I6 = alg_to_pos('i6');
        I7 = alg_to_pos('i7'); I8 = alg_to_pos('i8');

        K1 = alg_to_pos('k1'); K2 = alg_to_pos('k2'); K3 = alg_to_pos('k3');
        K4 = alg_to_pos('k4'); K5 = alg_to_pos('k5'); K6 = alg_to_pos('k6');
        K7 = alg_to_pos('k7');

        L1 = alg_to_pos('l1'); L2 = alg_to_pos('l2'); L3 = alg_to_pos('l3');
        L4 = alg_to_pos('l4'); L5 = alg_to_pos('l5'); L6 = alg_to_pos('l6');

        for k, alg in enumerate(BOARD_SPACE_NAMES):
            setattr(cls, alg, alg_to_pos(alg))

        # ========================================

        # Define initial placement of pieces,
        #   using multiple representations.
        #
        PAWN_HOME_BLACK = [B7, C7, D7, E7, F7, G7, H7, I7, K7]
        PAWN_HOME_WHITE = [B1, C2, D3, E4, F5, G4, H3, I2, K1]
        INIT_PIECES_DICT = {
                Player.Black: {
                    PieceType.King:   [G10],
                    PieceType.Queen:  [E10],
                    PieceType.Rook:   [C8, I8],
                    PieceType.Bishop: [F11, F10, F9],
                    PieceType.Knight: [D9, H9],
                    PieceType.Pawn:   PAWN_HOME_BLACK,
                },
                Player.White: {
                    PieceType.King:   [G1],
                    PieceType.Queen:  [E1],
                    PieceType.Rook:   [C1, I1],
                    PieceType.Bishop: [F3, F2, F1],
                    PieceType.Knight: [D1, H1],
                    PieceType.Pawn:   PAWN_HOME_WHITE,
                }
                }
        setattr(cls, "INIT_PIECES_DICT", INIT_PIECES_DICT)


        INIT_PIECES_FEN = "6/p5P/rp4PR/n1p3P1N/q2p2P2Q/bbb1p1P1BBB/k2p2P2K/n1p3P1N/rp4PR/p5P/6 w - - 0 1"
        setattr(cls, "INIT_PIECES_FEN", INIT_PIECES_FEN)

        INIT_PIECES_LIST = list("""
                      -   -   -   -   -   -
                    p   -   -   -   -   -   P
                  r   p   -   -   -   -   P   R
                n   -   p   -   -   -   P   -   N
              q   -   -   p   -   -   P   -   -   Q
            b   b   b   -   p   -   P   -   B   B   B
              k   -   -   p   -   -   P   -   -   K
                n   -   p   -   -   -   P   -   N
                  r   p   -   -   -   -   P   R
                    p   -   -   -   -   -   P
                      -   -   -   -   -   -
             """.split())
        setattr(cls, "INIT_PIECES_LIST", INIT_PIECES_LIST)

        # ========================================

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
        VECS_PAWN_ADV_BLACK: HexVec = VEC6
        VECS_PAWN_ADV_WHITE: HexVec = VEC0

        VECS_PAWN_CAPT_BLACK: List[HexVec] = [VEC4, VEC8]
        VECS_PAWN_CAPT_WHITE: List[HexVec] = [VEC2, VEC10]

        VECS_PAWN_HOP_BLACK: HexVec = 2 * VEC6
        VECS_PAWN_HOP_WHITE: HexVec = 2 * VEC0

        setattr(cls, "VECS_PAWN_ADV_BLACK",  VECS_PAWN_ADV_BLACK)
        setattr(cls, "VECS_PAWN_ADV_WHITE",  VECS_PAWN_ADV_WHITE)

        setattr(cls, "VECS_PAWN_CAPT_BLACK", VECS_PAWN_CAPT_BLACK)
        setattr(cls, "VECS_PAWN_CAPT_WHITE", VECS_PAWN_CAPT_WHITE)

        setattr(cls, "VECS_PAWN_HOP_BLACK",  VECS_PAWN_HOP_BLACK)
        setattr(cls, "VECS_PAWN_HOP_WHITE",  VECS_PAWN_HOP_WHITE)

        # ========================================
        LEAPS_KING = {}
        for npos in range(SPACE_COUNT):
            pos = cls.npos_to_pos(npos)
            npos_leap = [cls.pos_to_npos(pos + vec)
                        for vec in VECS_12
                        if cls.is_pos_on_board(pos + vec)]
            LEAPS_KING[npos] = npos_leap
        setattr(cls, "LEAPS_KING", LEAPS_KING)

        LEAPS_KNIGHT = {}
        for npos in range(SPACE_COUNT):
            pos = cls.npos_to_pos(npos)
            npos_leap = [cls.pos_to_npos(pos + vec)
                        for vec in VECS_KNIGHT
                        if cls.is_pos_on_board(pos + vec)]
            LEAPS_KNIGHT[npos] = npos_leap
        setattr(cls, "LEAPS_KNIGHT", LEAPS_KNIGHT)

        # ========================================
        #
        # This section could likely be more compact, at the cost of clarity.
        #
        LEAP_PAWN_ADV_BLACK = {}
        for npos in range(SPACE_COUNT):
            if BB_COURT_BLACK[npos] or BB_PROMO_BLACK[npos]:
                continue
            pos = cls.npos_to_pos(npos)
            pos_adv = pos + VECS_PAWN_ADV_BLACK
            LEAP_PAWN_ADV_BLACK[npos] = cls.pos_to_npos(pos_adv)
        setattr(cls, "LEAP_PAWN_ADV_BLACK", LEAP_PAWN_ADV_BLACK)

        LEAP_PAWN_ADV_WHITE = {}
        for npos in range(SPACE_COUNT):
            if BB_COURT_WHITE[npos] or BB_PROMO_WHITE[npos]:
                continue
            pos = cls.npos_to_pos(npos)
            pos_adv = pos + VECS_PAWN_ADV_WHITE
            LEAP_PAWN_ADV_WHITE[npos] = cls.pos_to_npos(pos_adv)
        setattr(cls, "LEAP_PAWN_ADV_WHITE", LEAP_PAWN_ADV_WHITE)

        # --------------------

        LEAP_PAWN_CAPT_BLACK = {}
        for npos in range(SPACE_COUNT):
            if BB_COURT_BLACK[npos] or BB_PROMO_BLACK[npos]:
                continue
            pos = cls.npos_to_pos(npos)
            npos_capt = [cls.pos_to_npos(pos + vec)
                        for vec in VECS_PAWN_CAPT_BLACK
                        if cls.is_pos_on_board(pos + vec)]
            LEAP_PAWN_CAPT_BLACK[npos] = npos_capt
        setattr(cls, "LEAP_PAWN_CAPT_BLACK", LEAP_PAWN_CAPT_BLACK)

        LEAP_PAWN_CAPT_WHITE = {}
        for npos in range(SPACE_COUNT):
            if BB_COURT_WHITE[npos] or BB_PROMO_WHITE[npos]:
                continue
            pos = cls.npos_to_pos(npos)
            npos_capt = [cls.pos_to_npos(pos + vec)
                        for vec in VECS_PAWN_CAPT_WHITE
                        if cls.is_pos_on_board(pos + vec)]
            LEAP_PAWN_CAPT_WHITE[npos] = npos_capt
        setattr(cls, "LEAP_PAWN_CAPT_WHITE", LEAP_PAWN_CAPT_WHITE)

        # --------------------

        LEAP_PAWN_HOP_BLACK = {}
        for pos in PAWN_HOME_BLACK:
            npos = cls.pos_to_npos(pos)
            pos_hop = cls.npos_to_pos(npos) + VECS_PAWN_HOP_BLACK
            LEAP_PAWN_HOP_BLACK[npos] = cls.pos_to_npos(pos_hop)
        setattr(cls, "LEAP_PAWN_HOP_BLACK", LEAP_PAWN_HOP_BLACK)

        LEAP_PAWN_HOP_WHITE = {}
        for pos in PAWN_HOME_WHITE:
            npos = cls.pos_to_npos(pos)
            pos_hop = cls.npos_to_pos(npos) + VECS_PAWN_HOP_WHITE
            LEAP_PAWN_HOP_WHITE[npos] = cls.pos_to_npos(pos_hop)
        setattr(cls, "LEAP_PAWN_HOP_WHITE", LEAP_PAWN_HOP_WHITE)

        # ========================================

        # When moving a slider, check space in progression,
        # until the piece moves off the board or contacts a piece.
        # Called by get_moves_pseudolegal_slider().
        # Pre-compute this, so rays can be found by lookup.
        def get_ray(pos: HexPos, vec: HexVec) -> List[Npos]:
            result = []
            cursor = pos
            for _ in range(11):
                cursor = cursor + vec
                if cls.is_pos_on_board(cursor):
                    result.append(cls.pos_to_npos(cursor))
                else:
                    return result

        def get_rays(pos: HexPos, vecs: List[HexVec]) -> List[List[Npos]]:
            result = []
            for vec in vecs:
                ray = get_ray(pos, vec)
                if ray:  # Do not append zero-length rays.
                    result.append(ray)
            return result

        RAYS_BISHOP = {}
        for npos in range(SPACE_COUNT):
            pos = HexPos(COORD_HEX0[npos], COORD_HEX1[npos])
            RAYS_BISHOP[npos] = get_rays(pos, VECS_DIAG)
        setattr(cls, "RAYS_BISHOP", RAYS_BISHOP)

        RAYS_QUEEN = {}
        for npos in range(SPACE_COUNT):
            pos = HexPos(COORD_HEX0[npos], COORD_HEX1[npos])
            RAYS_QUEEN[npos] = get_rays(pos, VECS_12)
        setattr(cls, "RAYS_QUEEN", RAYS_QUEEN)

        RAYS_ROOK = {}
        for npos in range(SPACE_COUNT):
            pos = HexPos(COORD_HEX0[npos], COORD_HEX1[npos])
            RAYS_ROOK[npos] = get_rays(pos, VECS_ORTHO)
        setattr(cls, "RAYS_ROOK", RAYS_ROOK)

    # ========================================
    # ========================================

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

    # get_space_color() would be a more specific name,
    # but get_board_color() is more idiomatic.
    @classmethod
    def get_board_color(cls, npos: Npos) -> BoardColor:
        pos = cls.npos_to_pos(npos)
        return BoardColor((pos.hex0 + pos.hex1) % 3)

    @classmethod
    def is_pos_on_board(cls, pos: HexPos):
        # Board corner       hex1 - hex0
        # NE: HexPos( 5,  5)      0
        # N:  HexPos( 0,  5)      5
        # NW: HexPos(-5,  0)      5
        # SE: HexPos( 5,  0)     -5
        # S:  HexPos( 0, -5)     -5
        # SW: HexPos(-5, -5)      0

        result = (
            -5 <= pos.hex0 <= 5      # W --> E
            and -5 <= pos.hex1 <= 5  # SW --> NE
            and -5 <= pos.hex1 - pos.hex0 <= 5  # SE --> NW
        )
        return result

    # ========================================
    # Conversion routines
    #
    @classmethod
    def alg_to_npos(cls, alg: str) -> str:
        return cls.pos_to_npos(cls.alg_to_pos(alg))

    @classmethod
    def npos_to_alg(cls, npos: Npos) -> str:
        return cls.BOARD_SPACE_NAMES[npos].lower()

    @classmethod
    def npos_to_pos(cls, npos: Npos) -> str:
        return HexPos(cls.COORD_HEX0[npos], cls.COORD_HEX1[npos])

    @classmethod
    def pos_to_alg(cls, pos: HexPos) -> str:
        file_char = cls.FILE_CHARS[pos.hex0 + 5]
        rank = 6 - max(0, pos.hex0) + pos.hex1
        return file_char + str(rank)

    @classmethod
    def pos_to_npos(cls, pos: HexPos) -> Npos:
        npos = cls.COORDS_TO_NPOS[(pos.hex0, pos.hex1)]
        return npos
