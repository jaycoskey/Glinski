#!/usr/bin/env python
# by Jay M. Coskey, 2026

import re
from typing import Dict, Generator, Iterable, List

from src.bitboard import BB_COURT_BLACK, BB_COURT_WHITE
from src.board_color import BoardColor
from src.geometry import Geometry as G
from src.hex_vec import HexVec
from src.hex_pos import HexPos
from src.move import Move
from src.piece import Piece
from src.piece_type import PieceType, PIECE_TYPE_COUNT
from src.player import Player, PLAYER_COUNT
from src.zobrist import ZOBRIST_HASH_TABLE

Npos = int


class Board:
    # Different ways to initialize board:
    #   * By data showing piece placements by color and piece type:
    #         placements: Dict[Player, Dict[PieceType, List[Pos]]]
    #   * By a FEN string:
    #         placements: str
    def __init__(self, placements=None):
        if placements is None:
            placements = G.INIT_PIECES_DICT

        self.pieces = [None for k in range(G.SPACE_COUNT)]
        for player in placements.keys():
            for pt in placements[player].keys():
                for pos in placements[player][pt]:
                    # piece_name = f'{player.name} {pt.name}'
                    # space_name = f'{G.pos_to_alg(pos)}=HexPos{pos}'
                    # print(f'INFO: adding ({piece_name:<12}) to {space_name}')
                    self.piece_add(pos, player, pt)

        self.cur_player = None  # TODO
        self.halfmove_counter = None  # TODO
        self.history_moves = None  # TODO
        self.history_nonprogress_halfmove_counts = None  # TODO
        self.history_ep_targets = None  # TODO
        self.history_zobrist_hashes = None  # TODO (Intentionlly not using Counter class)

    def find_mates_in_1(self):  # -> Generator[Move]
        moves = self.board.get_legal_moves()
        result = []
        for move in moves:
            b.move_make(move)
            if b.is_checkmate():
                result.append(move)
            b.move_undo(move)
        return result

    # Assume the next player to move is White
    # Returns a tree structure of moves, with depth 3:
    #   mates_in_2[m_p][m_opp][
    #   A first move, followed by a series of moves that brings about checkmate to the opponent.
    def find_mates_in_2(self)-> Dict:
        mates_in_2 = {}
        moves_p = self.get_legal_moves()
        for m_p in moves_p:
            inevitable_mates = find_mates_in_2_starting_with(m_p)
            if inevitable_mates:
                mates_in_2[m_p] = inevitable_mates
        return mates_in_2

    # p:   The Player who makes move m_p.
    # opp: The opponent of Player p. Player opp makes move m_opp.
    #
    def find_mates_in_2_starting_with(self, m_p):
        inevitable_mates = {}
        self.move_make(m_p)
        moves_opp = b.get_legal_moves()
        for m_opp in moves_opp:
            self.move_make(m_opp)
            if self.is_game_over():
                is_mate_avoidable = True
                sefl.move_undo(m_p)
                break
            else:
                mates_p = [m2_p for m2_p in b.get_legal_moves() if b.is_checkmate(m2_p)]
                if len(mates_p) == 0:
                    is_mate_avoidable = True
                    self.move_undo(m_opp)
                    break
                if not m_p in inevitable_mates:
                    inevitable_mates[m_opp] = mates_p
                    self.move_undo(m_opp)
        if is_mate_avoidable:
            return {}
        else:
            return inevitable_mates

    # ========================================

    def get_board_errors(self):
        raise NotImplementedError("board.get_board_errors()")

    def get_ep_target(self):
        raise NotImplementedError("board.get_ep_target()")

    def get_fen(self):
        raise NotImplementedError("board.get_fen()")

    # ========================================

    def get_leap_pawn_adv(self, npos: Npos) -> Npos:
        if self.cur_player == Player.Black:
            return G.LEAP_PAWN_ADV_BLACK[npos]
        else:
            return G.LEAP_PAWN_ADV_WHITE[npos]

    def get_leap_pawn_capt(self, npos: Npos) -> Iterable[Npos]:
        if self.cur_player == Player.Black:
            return G.LEAP_PAWN_CAPT_BLACK[npos]
        else:
            return G.LEAP_PAWN_CAPT_WHITE[npos]

    def get_leap_pawn_hop(self, npos: Npos) -> Npos:
        if self.cur_player == Player.Black:
            return G.LEAP_PAWN_HOP_BLACK[npos]
        else:
            return G.LEAP_PAWN_HOP_WHITE[npos]

    # ========================================

    def get_moves_legal(self):
        raise NotImplementedError("board.get_moves_legal()")

    def get_moves_legal_matching(self):
        raise NotImplementedError("board.get_moves_legal_matching()")

    def get_moves_pseudolegal(self, player=None):
        moves = []
        for npos in range(G.SPACE_COUNT):
            moves.extend(self.get_moves_pseudolegal_from(npos))
        return moves

    def get_moves_pseudolegal_from(self, npos: Npos):
        piece = self.pieces[npos]
        if piece is None or piece != self.cur_player:
            return []
        pt = piece.pt
        if pt in [PieceType.King, PieceType.KNIGHT]:
            print(f'Calling get_moves_pseudolegal_leaper()')
            moves = get_moves_pseudolegal_leaper(npos, pt)
        elif pt in [PieceType.Bishop, PieceType.Queen, PieceType.Rook]:
            print(f'Calling get_moves_pseudolegal_slider()')
            moves = get_moves_pseudolegal_slider(npos, pt)
        else:
            print(f'Calling get_moves_pseudolegal_pawn()')
            moves = get_moves_pseudolegal_pawn(npos)
        return moves

    def get_moves_pseudolegal_leaper(self, fr_npos: Npos, pt: PieceType) -> Iterable[Move]:
        fr_pos = G.npos_to_pos(npos)
        vecs_leaper = G.VECS_KING if pt == PieceType.King else G.VECS_KNIGHT
        for vec in vecs_leaper:
            to_pos = pos + vec
            to_npos = G.pos_to_npos(dest_pos)
            to_piece = self.pieces[dest_npos]
            if to_piece is None:
                move = Move(fr_npos, to_npos, None)
                # TODO: Set to non-capture
                yield move
            elif to_piece.player == self.cur_player.opponent():
                move = Move(fr_npos, to_npos, None)
                # TODO: Set to capture
                yield move

    # TODO: Allow for selection of promo_pt on Pawn promotion
    def get_moves_pseudolegal_pawn(self, npos: Npos) -> Iterable[Move]:
        pos = G.npos_to_pos(npos)
        fwd1_pos = pos + VEC_PAWN_ADV
        assert(self.is_pos_on_board(fwd1_pos))
        fwd1_npos = G.pos_to_npos(fwd1_pos)
        fwd1_piece = self.pieces[fwd1_npos]
        if not fwd1_piece:
            move = Move(npos, fwd1_npos, None)
            yield move
            if fwd1_npos in self.is_in_pawn_home(fwd1_npos):
                fwd2_npos = self.get_leap_pawn_hop(npos)
                fwd2_piece = self.pieces[fwd2_npos]
                if not fwd2_piece:
                    move = Move(npos, fwd2_npos, None)
                    yield move
        for capt_npos in get_leap_pawn_capt(npos):
            if capt_npos == self.ep_target:
                yield Move(npos, capt_npos, None)
            else:
                capt_piece = self.pieces[capt_npos]
                if capt_piece and capt_piece.player == self.cur_player.opponent():
                    move = Move(npos, capt_npos, None)
                    yield Move

    def get_moves_pseudolegal_slider(self, npos: Npos, pt: PieceType):
        if pt == PieceType.Queen:
            rays = RAYS_QUEEN
        elif pt == PieceType.Rook:
            rays = RAYS_ROOK
        else:
            rays = RAYS_BISHOP

        for ray in rays:
            for posn in ray:
                dest_piece = self.pieces[posn]
                if dest_piece is None:
                    move = Move(fr_posn, to_posn)
                    # Set to non-capture
                    yield move
                    continue
                dest_player = dest_piece.player
                if dest_player == self.cur_player.opponent():
                    move = Move(fr_posn, to_posn)
                    # Set to capture
                    yield move
                    break
                break

    def get_piece(self, npos: Npos):
        return self.pieces[npos]

    def get_pieces(self, player: Player):
        raise NotImplementedError("board.get_pieces()")

    def get_pieces_at_file(self, pt: PieceType, f: str):
        raise NotImplementedError("board.get_pieces_at_file()")

    def get_pieces_at_rank(self, pt: PieceType, r: int):
        raise NotImplementedError("board.get_pieces_at_rank()")

    def get_pieces_list(self, pt: PieceType, r: int):
        raise NotImplementedError("board.get_pieces_list()")

    def get_pieces_map(self):
        raise NotImplementedError("board.get_pieces_map()")

    # ========================================

    def get_print_str(self, indent_board=8, indent_incr=2, item_width=4):
        result_rows = []

        ROWS = [[                     40                     ],
                [                 30,     51                 ],
                [             21,     41,     61             ],
                [         13,     31,     52,     70         ],
                [      6,     22,     42,     62,     78     ],
                [  0,     14,     32,     53,     71,     85 ],
                [      7,     23,     43,     63,     79     ],
                [  1,     15,     33,     54,     72,     86 ],
                [      8,     24,     44,     64,     80     ],
                [  2,     16,     34,     55,     73,     87 ],
                [      9,     25,     45,     65,     81,    ],
                [  3,     17,     35,     56,     74,     88 ],
                [     10,     26,     46,     66,     82,    ],
                [  4,     18,     36,     57,     75,     89 ],
                [     11,     27,     47,     67,     83     ],
                [  5,     19,     37,     58,     76,     90 ],
                    [ 12 ,    28,     48,     68,     84 ],
                        [ 20,     38,     59,     77 ],
                            [ 29,     49,     69 ],
                                [ 39,     60 ],
                                    [ 50 ]]

        def row_indent_size(row_num):
            result = indent_board
            rows_from_middle = abs(10 - row_num)
            if rows_from_middle > 5:
                result += (rows_from_middle - 5) * indent_incr
            elif rows_from_middle % 2 == 0:
                result += indent_incr
            return result

        for row_num, row in enumerate(ROWS):
            row_str = row_indent_size(row_num) * ' '  # Indentation
            for item in row:
                index = int(item)
                piece = self.pieces[index]
                txt = str(piece) if piece else '-'
                row_str += str(txt.ljust(item_width))
            result_rows.append(row_str.rstrip())  # End of row
        return '\n'.join(result_rows)

    # When moving a slider, check space in progression,
    # until the piece moves off the board or contacts a piece.
    # Called by get_moves_pseudolegal_slider().
    # TODO: Pre-compute this, so rays can be found by lookup.
    def get_ray(p: HexPos, v: HexVec):
        result = []
        cursor = p
        for k in range(0, 10):
            cursor = cursor + v
            if is_pos_on_board(cursor):
                result.append(cursor)
            else:
                return result

    # For each piece on the Board, there is a corresponding unique triple:
    #   (Board position ID, player ID, piece_type ID).
    # That is used to look up a value in the ZobristHashTable that
    # corresponds to that triplet.
    #   * The Board position ID (npos) selects a plane.
    #   * The Player value (p_val) selects a row within that plane.
    #   * The PieceType value (p_val) selects a column within that plane.
    # All such values are XORed together to form the final result.
    def get_zobrist_hash(self):
        result = 0
        for npos in range(G.SPACE_COUNT):
            piece = self.get_piece(npos)
            if piece:
                p_val = piece.player.value
                pt_val = piece.pt.value
                zobrist_index = (npos * PLAYER_COUNT * PIECE_TYPE_COUNT
                    + p_val * PIECE_TYPE_COUNT + pt_val)
                result ^= ZOBRIST_HASH_TABLE[zobrist_index]
        return result

    # ========================================
    # TODO: Fetch info cached at time move is made

    def is_condition_check(self):
        raise NotImplementedError("board.is_condition_check()")

    # TODO: Fetch info cached at time move is made
    def is_condition_checkmate(self):
        raise NotImplementedError("board.is_condition_checkmate()")

    # TODO: Fetch info cached at time move is made
    def is_condition_dead_position(self):
        raise NotImplementedError("board.is_condition_dead_position()")

    # TODO: Fetch info cached at time move is made
    def is_condition_insufficient_material(self):
        raise NotImplementedError("board.is_condition_insufficient_material()")

    # Note: history_nonprogress_halfmove_counts is updated at Move time
    def is_condition_nonprogress_moves_50(self):
        when = self.halfmove_count
        return self.history_nonprogress_halfmove_counts[when] >= 100

    # Note: history_nonprogress_halfmove_counts is updated at Move time
    def is_condition_nonprogress_moves_75(self):
        when = self.halfmove_count
        return self.history_nonprogress_halfmove_counts[when] >= 150

    # TODO: Fetch info cached at time move is made
    def is_condition_repetition_3x(self):
        counter = Counter(self.history_zobrist_hashes[0:self.halfmove_count + 1])
        return max(counter.values()) >= 3

    # TODO: Fetch info cached at time move is made
    def is_condition_repetition_5x(self):
        counter = Counter(self.history_zobrist_hashes[0:self.halfmove_count + 1])
        return max(counter.values()) >= 5

    # TODO: Fetch info cached at time move is made
    def is_condition_stalemate(self):
        # return len(self.get_legal_moves()) == 0
        raise NotImplementedError("board.is_condition_stalemate()")

    # ========================================
    # Tests on individual spaces or pieces
    #
    def is_empty(self, npos: Npos):
        return self.pieces[npos] is None

    def is_ep_target(self, npos: Npos):
        return npos == self.ep_target

    def is_in_court_zone(self, npos: Npos):
        if self.cur_player == Player.Black:
            return BB_COURT_BLACK[npos]
        else:
            return BB_COURT_WHITE[npos]

    def is_in_pawn_home_zone(self, npos: Npos):
        if self.cur_player == Player.Black:
            return INIT_PAWN_HOME_BLACK[npos]
        else:
            return INIT_PAWN_HOME_WHITE[npos]

    def is_in_pawn_promo_zone(self, npos: Npos):
        if self.cur_player == Player.Black:
            return PAWN_PROMO_BLACK[npos]
        else:
            return PAWN_PROMO_WHITE[npos]

    # ========================================

    def is_move_pseudolegal(m: Move):
        raise NotImplementedError("board.is_move_pseudolegal()")

    # Called by is_condition_check() / is_condition_checkmate()
    # When player=None, player=self.cur_player is assumed.
    # In theory, player=self.cur_player.opponent() could be used
    #   to detect the error condition in which the opponent of
    #   the player moving is already in "check".
    def is_king_attacked(self, player=None):
        raise NotImplementedError("board.is_king_attacked()")

    # Check whether cur_player's King is being attacked.
    # When do_check_pseudolegal=False, pseudolegality is presumed.
    # Consider adding player=self.cur_player param for sanity check
    #     to determine whether last move left own King attacked.
    def is_move_legal(self, m: Move, do_check_pseudolegality=False):
        if do_check_pseudolegality:
            pseudolegal = self.is_move_pseudolegal(m)
            if not pseudolegal:
                return False
        b.move_make(m)
        is_legal = not b.is_king_attacked()
        b.move_undo(m)
        return is_legal

    # ========================================

    # Convenience method
    def is_pos_on_board(self, pos: HexPos):
        return G.is_pos_on_board(pos)

    # ========================================

    def move_make(self, m):
        raise NotImplementedError("board.move_make()")
        # Phases of Move execution, not including checking for legality:
        #   Capture. Remove destination piece (incl. en passant)
        #   Move.
        #     Move-piece1. Move piece.
        #     Move-piece2. (If castling in a variant that supports it, move Rook.)
        #     Promote. If promotion, swap Pawn for promotion piece.
        #   Update history [designed to support Move undo]:
        #     old_count = history_nonprogress_halfmove_counts[self.halfmove_count]
        #     Update halfmove_count += 1
        #     Update history stacks:
        #       (a) history_checks
        #       (b) history_checkmates  # Added to support move.redo(), which advances a half-step forward
        #       (c) history_ep_targets.append(ep_target if ep_target else None)
        #       (d) history_moves.append(m)
        #       (e) is_progress_move = m.is_progress_move (m.is_capture() or m.pt == PieceType.Pawn)
        #           history_nonprogress_halfmove_counts.append(0 if is_progress_move else old_count + 1)
        #       (f) history_zobrist_hashes.append(self.get_zobrist_hash())
        #   Update conditions:
        #     Set flags in board.game_conditions:GameConditions
        #       is_check
        #       is_checkmate
        #       is_ep_target = bool(self.ep_target)
        #       is nonprogress_halfmove_count_50 = history_nonprogress_halfmove_count[self.halfmove_count] >= 100
        #       is nonprogress_halfmove_count_75 = history_nonprogress_halfmove_count[self.halfmove_count] >= 150
        #       is_board_repetition_3x = max(Counter(history_zobrist_hashes).values()) >= 3
        #       is_board_repetition_5x = max(Counter(history_zobrist_hashes).values()) >= 5
        #   End of game
        #     game_over = (checkmate | stalemate | 75-move-rule | 5x board repetition
        #                     | offer & acceptance of end of game)
        #     if game_over:
        #       Update Termination info, including game_state = GameState.IsOver
        #     if is_checkmate or is_check:
        #       Notify opponent.

    def move_undo(self, m):
        raise NotImplementedError("board.move_undo()")
        # Revert GameState. If GameState = GameState.Over,
        #  then revert to GameState.InProgress. Clear any win/draw details.
        # Truncate history. Call pop on history stacks:
        #   (a) checks, (b) checkmates, (c) ep targets, (d) moves,
        #   (e) nonprogress halfmove counts, (f) zobrish hashes()
        # Reset BoardCondition states from the history stacks.
        # Unpromote.      If promotion, swap promoted piece for original Pawn.
        # Unmove-piece2.  If Move was castling, move Rook back.
        # Unmove-piece1.  Move primary piece back to original space.
        # Uncapture.      If move was capture, restore removed piece.

    def moves_make(self, ms):
        raise NotImplementedError("board.moves_make()")

    def moves_undo(self, ms):
        raise NotImplementedError("board.moves_undo()")

    # ========================================

    # Note that the piece addition is done via pos, but removal uses npos.
    def piece_add(self, pos: HexPos, player: Player, pt: PieceType):
        npos = G.pos_to_npos(pos)
        self.pieces[npos] = Piece(player, pt)

    # Note that the piece addition is done via pos, but removal uses npos.
    def piece_remove(self, npos: Npos, player: Player=None, pt: PieceType=None):
        self.pieces[npos] = None

    # ========================================

    def print(self, indent_board=8, indent_incr=2, item_width=4):
        text = self.get_print_str(indent_board, indent_incr, item_width)
        print(text)

    # For each move, info such as is_check() and is_repetition_3x()
    # should be cached so it is not re-computed multiple times.
    # This method stores and caches that info.
    # Should there be a separate mode for find-mate-in-two puzzles,
    #   ignoring certain end-game conditions?
    def set_board_conditions(self):
        raise NotImplementedError("board.set_board_conditions()")
