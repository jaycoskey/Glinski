#!/usr/bin/env python
# by Jay M. Coskey, 2026

from bitarray import bitarray

BitBoard = bitarray

# ========================================

BB_A6 = BitBoard(91); BB_A5 = BitBoard(91); BB_A4 = BitBoard(91);
BB_A3 = BitBoard(91); BB_A2 = BitBoard(91); BB_A1 = BitBoard(91);

BB_B7 = BitBoard(91); BB_B6 = BitBoard(91); BB_B5 = BitBoard(91);
BB_B4 = BitBoard(91); BB_B3 = BitBoard(91); BB_B2 = BitBoard(91);
BB_B1 = BitBoard(91);

BB_C8 = BitBoard(91); BB_C7 = BitBoard(91); BB_C6 = BitBoard(91);
BB_C5 = BitBoard(91); BB_C4 = BitBoard(91); BB_C3 = BitBoard(91);
BB_C2 = BitBoard(91); BB_C1 = BitBoard(91);

BB_D9 = BitBoard(91); BB_D8 = BitBoard(91); BB_D7 = BitBoard(91);
BB_D6 = BitBoard(91); BB_D5 = BitBoard(91); BB_D4 = BitBoard(91);
BB_D3 = BitBoard(91); BB_D2 = BitBoard(91); BB_D1 = BitBoard(91);

BB_E10 = BitBoard(91); BB_E9 = BitBoard(91); BB_E8 = BitBoard(91);
BB_E7 = BitBoard(91); BB_E6 = BitBoard(91); BB_E5 = BitBoard(91);
BB_E4 = BitBoard(91); BB_E3 = BitBoard(91); BB_E2 = BitBoard(91);
BB_E1 = BitBoard(91);

BB_F11 = BitBoard(91); BB_F10 = BitBoard(91); BB_F9 = BitBoard(91);
BB_F8 = BitBoard(91); BB_F7 = BitBoard(91); BB_F6 = BitBoard(91);
BB_F5 = BitBoard(91); BB_F4 = BitBoard(91); BB_F3 = BitBoard(91);
BB_F2 = BitBoard(91); BB_F1 = BitBoard(91);

BB_G10 = BitBoard(91); BB_G9 = BitBoard(91); BB_G8 = BitBoard(91);
BB_G7 = BitBoard(91); BB_G6 = BitBoard(91); BB_G5 = BitBoard(91);
BB_G4 = BitBoard(91); BB_G3 = BitBoard(91); BB_G2 = BitBoard(91);
BB_G1 = BitBoard(91);

BB_H9 = BitBoard(91); BB_H8 = BitBoard(91); BB_H7 = BitBoard(91);
BB_H6 = BitBoard(91); BB_H5 = BitBoard(91); BB_H4 = BitBoard(91);
BB_H3 = BitBoard(91); BB_H2 = BitBoard(91); BB_H1 = BitBoard(91);

BB_I8 = BitBoard(91); BB_I7 = BitBoard(91); BB_I6 = BitBoard(91);
BB_I5 = BitBoard(91); BB_I4 = BitBoard(91); BB_I3 = BitBoard(91);
BB_I2 = BitBoard(91); BB_I1 = BitBoard(91);

BB_K7 = BitBoard(91); BB_K6 = BitBoard(91); BB_K5 = BitBoard(91);
BB_K4 = BitBoard(91); BB_K3 = BitBoard(91); BB_K2 = BitBoard(91);
BB_K1 = BitBoard(91);

BB_L6 = BitBoard(91); BB_L5 = BitBoard(91); BB_L4 = BitBoard(91);
BB_L3 = BitBoard(91); BB_L2 = BitBoard(91); BB_L1 = BitBoard(91);

BITBOARD_SPACES = [BB_A6, BB_A5, BB_A4, BB_A3, BB_A2, BB_A1,
        BB_B7, BB_B6, BB_B5, BB_B4, BB_B3, BB_B2, BB_B1,
        BB_C8, BB_C7, BB_C6, BB_C5, BB_C4, BB_C3, BB_C2, BB_C1,
        BB_D9, BB_D8, BB_D7, BB_D6, BB_D5, BB_D4, BB_D3, BB_D2, BB_D1,
        BB_E10, BB_E9, BB_E8, BB_E7, BB_E6, BB_E5, BB_E4, BB_E3, BB_E2, BB_E1,
        BB_F11, BB_F10, BB_F9, BB_F8, BB_F7, BB_F6, BB_F5, BB_F4, BB_F3, BB_F2, BB_F1,
        BB_G10, BB_G9, BB_G8, BB_G7, BB_G6, BB_G5, BB_G4, BB_G3, BB_G2, BB_G1,
        BB_H9, BB_H8, BB_H7, BB_H6, BB_H5, BB_H4, BB_H3, BB_H2, BB_H1,
        BB_I8, BB_I7, BB_I6, BB_I5, BB_I4, BB_I3, BB_I2, BB_I1,
        BB_K7, BB_K6, BB_K5, BB_K4, BB_K3, BB_K2, BB_K1,
        BB_L6, BB_L5, BB_L4, BB_L3, BB_L2, BB_L1]

for k in range(len(BITBOARD_SPACES)):
    BITBOARD_SPACES[k][k] = True

def npos_to_bb(npos: int):
    return BITBOARD_SPACES[npos]

# ========================================

BB_CORNERS = BB_A6 | BB_A1 | BB_F11 | BB_F1 | BB_L6 | BB_L1

# ========================================
# In Glinski's Hexagonal Chess, "courts" are the spaces behind
# the initial pawn locations, where the King and Queen reside.
# A representation of this can be useful in detecting the Board
#   layout error of Pawns being behind their initial home positions.
BB_COURT_BLACK = (BB_C8
        | BB_D9 | BB_D8
        | BB_E10 | BB_E9 | BB_E8
        | BB_F11 | BB_F10 | BB_F9 | BB_F8
        | BB_G10 | BB_G9 | BB_G8
        | BB_H9 | BB_H8
        | BB_I8)

BB_COURT_WHITE = (BB_C1
        | BB_D2 | BB_D1
        | BB_E3 | BB_E2 | BB_E1
        | BB_F4 | BB_F3 | BB_F2 | BB_F1
        | BB_G3 | BB_G2 | BB_G1
        | BB_H2 | BB_H2
        | BB_I1)

# ========================================

BB_EDGE_NE = BB_F11 | BB_G10 | BB_H9 | BB_I8 | BB_K7 | BB_L6
BB_EDGE_NW = BB_A6 | BB_B7 | BB_C8 | BB_D9 | BB_E10 | BB_F11
BB_EDGE_E  = BB_L6 | BB_L5 | BB_L4 | BB_L3 | BB_L2 | BB_L1
BB_EDGE_SE = BB_F1 | BB_G1 | BB_H1 | BB_I1 | BB_L1 | BB_L1
BB_EDGE_SW = BB_A1 | BB_B1 | BB_C1 | BB_D1 | BB_E1 | BB_F1
BB_EDGE_W  = BB_A6 | BB_A5 | BB_A4 | BB_A3 | BB_A2 | BB_A1

BITBOARD_EDGES = [BB_EDGE_NE, BB_EDGE_NW, BB_EDGE_E,
        BB_EDGE_SE, BB_EDGE_SW, BB_EDGE_W]

# ========================================

BB_FILE_A = (BB_A6 | BB_A5 | BB_A4 | BB_A3 | BB_A2 | BB_A1)
BB_FILE_B = (BB_B7 | BB_B6 | BB_B5 | BB_B4 | BB_B3 | BB_B2
        | BB_B1)
BB_FILE_C = (BB_C8 | BB_C7 | BB_C6 | BB_C5 | BB_C4 | BB_C3
        | BB_C2 | BB_C1)
BB_FILE_D = (BB_D9 | BB_D8 | BB_D7 | BB_D6 | BB_D5 | BB_D4
        | BB_D3 | BB_D2 | BB_D1)
BB_FILE_E = (BB_E10 | BB_E9 | BB_E8 | BB_E7 | BB_E6 | BB_E5
        | BB_E4 | BB_E3 | BB_E2 | BB_E1)
BB_FILE_F = (BB_F11 | BB_F10 | BB_F9 | BB_F8 | BB_F7 | BB_F6
        | BB_F5 | BB_F4 | BB_F3 | BB_F2 | BB_F1)
BB_FILE_G = (BB_G10 | BB_G9 | BB_G8 | BB_G7 | BB_G6 | BB_G5
        | BB_G4 | BB_G3 | BB_G2 | BB_G1)
BB_FILE_H = (BB_H9 | BB_H8 | BB_H7 | BB_H6 | BB_H5 | BB_H4
        | BB_H3 | BB_H2 | BB_H1)
BB_FILE_I = (BB_I8 | BB_I7 | BB_I6 | BB_I5 | BB_I4 | BB_I3
        | BB_I2 | BB_I1)
BB_FILE_K = (BB_K7 | BB_K6 | BB_K5 | BB_K4 | BB_K3 | BB_K2
        | BB_K1)
BB_FILE_L = (BB_L6 | BB_L5 | BB_L4 | BB_L3 | BB_L2 | BB_L1)

BITBOARD_FILES = [
        BB_FILE_A, BB_FILE_B, BB_FILE_C, BB_FILE_D,
        BB_FILE_E, BB_FILE_F, BB_FILE_G, BB_FILE_H,
        BB_FILE_I, BB_FILE_K, BB_FILE_L]

# ========================================
BB_PAWN_HOME_BLACK = (BB_B7 | BB_C7 | BB_D7 | BB_E7
        | BB_F7
        | BB_G7 | BB_H7 | BB_I7 | BB_K7)

BB_PAWN_HOME_WHITE = (BB_B1 | BB_C2 | BB_D3 | BB_E4
        | BB_F5
        | BB_G4 | BB_H3 | BB_I2 | BB_K1)

# ========================================
BB_PROMO_BLACK = (BB_A1 | BB_B1 | BB_C1 | BB_D1 | BB_E1
        | BB_F1
        | BB_G1 | BB_H1 | BB_I1 | BB_K1 | BB_L1)

BB_PROMO_WHITE = (BB_A6 | BB_B7 | BB_C8 | BB_D9 | BB_E10
        | BB_F11
        | BB_G10 | BB_H9 | BB_I8 | BB_K7 | BB_L6)

# ========================================

BB_RING0 = BB_F6

BB_RING1 = BB_E6 | BB_E5 | BB_F7 | BB_F5 | BB_G6 | BB_G5

BB_RING2 = (BB_D6 | BB_D5 | BB_D4 | BB_E7 | BB_E4 | BB_F8
        | BB_F4 | BB_G7 | BB_G4 | BB_H6 | BB_H5 | BB_H4
        )

BB_RING3 = (BB_C6 | BB_C5 | BB_C4 | BB_C3 | BB_D7 | BB_D3
        | BB_E8 | BB_E3 | BB_F9 | BB_F3 | BB_G8 | BB_G3
        | BB_H7 | BB_H3 | BB_I6 | BB_I5 | BB_I4 | BB_I3
        )

BB_RING4 = (BB_B6 | BB_B5 | BB_B4 | BB_B3 | BB_B2 | BB_C7
        | BB_C2 | BB_D8 | BB_D2 | BB_E9 | BB_E2 | BB_F10
        | BB_F2 | BB_G9 | BB_G2 | BB_H8 | BB_H2 | BB_I7
        | BB_I2 | BB_K6 | BB_K5 | BB_K4 | BB_K3 | BB_K2)

# BB_RING5 could also be written as an OR of (BB) Board edges.
BB_RING5 = (BB_A6 | BB_A5 | BB_A4 | BB_A3 | BB_A2 | BB_A1
        | BB_B7 | BB_B1 | BB_C8 | BB_C1 | BB_D9 | BB_D1
        | BB_E10 | BB_E1 | BB_F11 | BB_F1 | BB_G10 | BB_G1
        | BB_H9 | BB_H1 | BB_I8 | BB_I1 | BB_K7 | BB_K1
        | BB_L6 | BB_L5 | BB_L4 | BB_L3 | BB_L2 | BB_L1)

BITBOARD_RINGS = [BB_RING0, BB_RING1, BB_RING2,
        BB_RING3, BB_RING4, BB_RING5]

# ========================================

BB_SPACES_LIGHT = (BB_A6 | BB_A3
        | BB_B5 | BB_B2
        | BB_C7 | BB_C4 | BB_C1
        | BB_D9 | BB_D6 | BB_D3
        | BB_E8 | BB_E5 | BB_E2
        | BB_F10 | BB_F7 | BB_F4 | BB_F1
        | BB_G8 | BB_G5 | BB_G2
        | BB_H9 | BB_H6 | BB_H3
        | BB_I7 | BB_I4 | BB_I1
        | BB_K5 | BB_K2
        | BB_L6 | BB_L3)

BB_SPACES_MEDIUM = (BB_A5 | BB_A2
        | BB_B7 | BB_B4 | BB_B1
        | BB_C6 | BB_C3
        | BB_D8 | BB_D5 | BB_D2
        | BB_E10 | BB_E7 | BB_E4 | BB_E1
        | BB_F9 | BB_F6 | BB_F3
        | BB_G10 | BB_G7 | BB_G4 | BB_G1
        | BB_H8 | BB_H5 | BB_H2
        | BB_I6 | BB_I3
        | BB_K7 | BB_K4 | BB_K1
        | BB_L5 | BB_L2)

BB_SPACES_DARK = (BB_A4 | BB_A1
        | BB_B6 | BB_B3
        | BB_C8 | BB_C5 | BB_C2
        | BB_D7 | BB_D4 | BB_D1
        | BB_E9 | BB_E6 | BB_E3
        | BB_F11 | BB_F8 | BB_F5 | BB_F2
        | BB_G9 | BB_G6 | BB_G3
        | BB_H7 | BB_H4 | BB_H1
        | BB_I8 | BB_I5 | BB_I2
        | BB_K6 | BB_K3
        | BB_L4 | BB_L1)

# ========================================

BB_WEFT0 = BB_F1
BB_WEFT1 = BB_E1 | BB_G1
BB_WEFT2 = BB_D1 | BB_F2 | BB_H1
BB_WEFT3 = BB_C1 | BB_E2 | BB_G2 | BB_I1
BB_WEFT4 = BB_B1 | BB_D2 | BB_F3 | BB_H2 | BB_K1
BB_WEFT5 = BB_A1 | BB_C2 | BB_E3 | BB_G3 | BB_I2 | BB_L1
BB_WEFT6 =     BB_B2 | BB_D3 | BB_F4 | BB_H3 | BB_K2
BB_WEFT7 = BB_A2 | BB_C3 | BB_E4 | BB_G4 | BB_I3 | BB_L2
BB_WEFT8 =     BB_B3 | BB_D4 | BB_F5 | BB_H4 | BB_K3
BB_WEFT9 = BB_A3 | BB_C4 | BB_E5 | BB_G5 | BB_I4 | BB_L3
BB_WEFT10 =    BB_B4 | BB_D5 | BB_F6 | BB_H5 | BB_K4
BB_WEFT11 = BB_A4 | BB_C5 | BB_E6 | BB_G6 | BB_I5 | BB_L4
BB_WEFT12 =    BB_B5 | BB_D6 | BB_F7 | BB_H6 | BB_K5
BB_WEFT13 = BB_A5 | BB_C6 | BB_E7 | BB_G7 | BB_I6 | BB_L5
BB_WEFT14 =    BB_B6 | BB_D7 | BB_F8 | BB_H7 | BB_K6
BB_WEFT15 = BB_A6 | BB_C7 | BB_E8 | BB_G8 | BB_I7 | BB_L6
BB_WEFT16 = BB_B7 | BB_D8 | BB_F9 | BB_H8 | BB_K7
BB_WEFT17 = BB_C8 | BB_E9 | BB_G9 | BB_I8
BB_WEFT18 = BB_D9 | BB_F10 | BB_H9
BB_WEFT19 = BB_E10 | BB_G10
BB_WEFT20 = BB_F11

BITBOARD_WEFTS = [
        BB_WEFT0, BB_WEFT1, BB_WEFT2, BB_WEFT3, BB_WEFT4,
        BB_WEFT5, BB_WEFT6, BB_WEFT7, BB_WEFT8, BB_WEFT9,
        BB_WEFT10, BB_WEFT11, BB_WEFT12, BB_WEFT13, BB_WEFT14,
        BB_WEFT15, BB_WEFT16, BB_WEFT17, BB_WEFT18, BB_WEFT19,
        BB_WEFT20]

