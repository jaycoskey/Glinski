<p align=center>Glinski<br/>by Jay M. Coskey<br/>2026-02-01</p>

## The board
Gliński's Hexagonal Chess is a variant of chess played on a board consisting of 91 hexagonal spaces.
Board diagrams and game rules can be found online here, here, and here, among other places.
The board for Glinski's hexagonal chess has 11 "files" (i.e., columns), commonly labeled a, b, c, d, e, f, g, i, k, l. As in standard chess, the spaces closest to White are considered to be in the first rank, and the numbering increases for spaces farther away.

Due to the shape of the board, the files at the sides of the board
(files 'a' and 'l') have 6 ranks each, while the center file (file 'f') has 11 rows.
Board spaces have alphanumeric descriptors, written as the file followed by the rank.
So the left-most file has spaces a1, a2 a3, a4, a5, a6; the right-most file has spaces l1, l2, l3, l4, l5, l6; and the middle file has spaces f1, f2, f3, f4, f5, f6 (the center of the board), f7, f8 ,f9 ,f10, f11.

The Board's spaces have three colors, commonly called Light, Medium, and Dark. The central space is Medium, which causes there to be 31 Medium spaces, 30 Light, and 30 Dark. The space closest to Player White's side of the Board is Light, while the space closest to Player Black is Dark.

## The rules
This variant works much like standard chess, except for the geometry.
* Rooks move in 6 directions. The corresponding directions on a clock face are 12, 2, 4, 6, 8, and 10 o'clock. These directions are commonly referred to as "orthogonal".
* There is one Bishop for each on one of the Board's 3 colors. These Bishops move in the directions of 1, 3, 5, 7, 9, and 11 o'clock. Thus the Bishop moves outward from its starting space along the "spokes" extending from its vertices. Each bishop remains on its board space color throughout the game. These directions are commonly referred to as "diagonal".
* Queens, of course, slide in any of the 12 directions of of the Rook or Bishop.
* Kings, of course, move one space in any of these 12 directions. There is no castling, but check and checkmate work exactly as in standard chess.
* Knights move two spaces like a rook, then turn 60 degrees, and move one more space.
* Pawns advance one space forward (or optionally two spaces from Pawn starting locations) when not capturing. They capture obliquely, in the 10 o'clock or 2 o'clock directions. When they reach the farthest rank in their current file, they get promoted to a Queen, Rook, Bishop, or Knight. *En passant* capture works as in standard chess.
* Stalemate is a partial win for the player who last moved. The stalemated player earns 1/4 of a point, while the last player to move earns 3/4 of a point.

## This software
This repository is intended to be a minimal chess engine for this variant. Top goals:
1. Allow a human to enter moves, have them checked for legality, and see ASCII, Unicode,
      or SVG views of the board state following those moves.
      Moves can be entered in a variety of ways, the simplest being what is called UCI format. (UCI = Universal Chess Interface.) In this format, each move is entered as a contiguous string of characters:
   * The starting space of the piece being moved (e.g., f10)
   * The ending space (e.g., g10)
   * (The act of capturing isn't called out in UCI format)
   * If the piece being moved is a Pawn, and it's being promoted on the last rank of its file, add on a letter to represent the piece type that the Pawn is being promoted to (q or Q for Queen, r or R for Rook, b or B for Bishop, n or N for Knight). So a Pawn moving from f10 to g10, capturing an opposing piece, and being promoted to a Queen would be written as f10g10q.
2. Store and load games, either as PGN files for full games, or as FEN strings for just the board layouts.
3. For any Board position and move, determine whether a game has ended. If it has not, find the set of legal moves available, which can be used to validate a human player's move, or can be used by a computer Player to select its next move.
4. Solve Glinski's Hexagonal Chess mate-in-two (or three, etc.) puzzles. This is a straightforward extension of a chess engine programmed with the rules of the game, and the ability to list available moves.
