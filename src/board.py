#!/usr/bin/env python
# by Jay M. Coskey, 2026
# pylint: disable=fixme, too-many-instance-attributes, too-many-public-methods

from bitarray import bitarray
from collections import Counter
from copy import deepcopy
import math
import os
from typing import Dict, Iterable, Iterator, List, Union

from src.bitboard import BB_COURT_BLACK, BB_COURT_WHITE
from src.bitboard import BB_PAWN_HOME_BLACK, BB_PAWN_HOME_WHITE
from src.bitboard import BB_PAWN_PROMO_BLACK, BB_PAWN_PROMO_WHITE
from src.bitboard import BITBOARD_FILES
from src.board_color import BoardColor
from src.board_error_flags import BoardErrorFlags
from src.board_state import BoardState
from src.game_state import GameState
from src.geometry import Geometry as G
from src.geometry import LayoutDict, Npos
from src.hex_pos import HexPos
from src.hex_vec import HexVec
from src.move import Move
from src.move_spec import MoveSpec
from src.piece import Piece
from src.piece_type import PieceType
from src.piece_type import PIECE_TYPES, PIECE_TYPE_COUNT, PROMO_PTS
from src.player import Player, PLAYER_COUNT
from src.zobrist import ZobristHash, ZOBRIST_TABLE


class Board:
    # ========================================
    # SECTION: CONSTRUCTOR
    # ========================================
    # Different ways to initialize board:
    #   * By a Layout structure (which can be empty, for an empty board)
    #   * By a FEN string
    # Note: An e.p. move executed in halfmove N (in move.ep_target)
    #   creates a Board ep_target in halfmove N+1 (in board.ep_target).
    def __init__(self, layout:Union[str, LayoutDict]=None):
        self.do_check_repetition = True
        if layout is None:
            layout_dict = deepcopy(G.INIT_LAYOUT_DICT)
            self.init_layout(layout_dict)
            self.init_defaults()
        elif type(layout) == dict:
            layout_dict = deepcopy(layout)
            self.init_layout(layout_dict)
            self.init_defaults()
        elif type(layout) == str:
            fen_parts = layout.split()
            if len(fen_parts) not in [1, 6]:
                msg = ('Board constructor: LayoutDict parameter appears '
                    + f'to be a FEN string with {len(fen_parts)} parts. '
                    + 'It should have 1 or 6.')
                raise ValueError(f'Board constructor: {msg}')
            if len(fen_parts) == 1:
                fen_board_str = fen_parts[0]
                layout_dict = G.fen_board_to_layout_dict(fen_board_str)
                self.init_layout(layout_dict)
                self.init_defaults()
            else:  # len(layout_chunks) == 6, so layout should be a full FEN string
                (fen_board_str, cur_player, ep_tgt_str,
                        nonprogress_ctr, fullmove_count,
                        halfmove_count) = Pgn.fen_to_fen_info(layout_fen)
                nones = [None] * (self.halfmove_count + 1)
                ind = self.halfmove_count

                # FEN part #1 (Board layout)
                layout_dict = G.fen_board_to_layout_dict(fen_board_str)
                self.init_layout(layout_dict)

                self.cur_player = cur_player  # FEN part #2

                # FEN part #3 regards castling, which is not allowed in Glinski's hexagonal chess.

                self.halfmove_count = halfmove_count  # FEN part #6

                self.history_ep_target = copy(nones)
                self.history_ep_target[ind] = None if ep_tgt_str == '-' else G.alg_to_npos(ep_tgt_str)  # FEN part #4

                self.history_nonprogress_halfmove_count[ind] = int(nonprogress_str)  # FEN part #5

                self.history_move = copy(nones)
                self.history_zobrist_hash = copy(nones)

                self.history_is_check = copy(nones)
                self.history_is_checkmate = copy(nones)
                self.history_is_repetition_3x = copy(nones)
                self.history_is_repetition_5x = copy(nones)
                self.history_is_stalemate = copy(nones)

                self.set_game_state(GameState.InPlay)
        else:
            ValueError('Board constructor arg has unrecognized type: '
                + f'{type(layout)}: {layout}')

    def init_defaults(self) -> None:
        # Board layout is addressed elsewhere.
        ####################
        # Info that is provided by a FEN string.
        ####################
        self.cur_player = Player.White
        self.halfmove_count = 0
        self.history_nonprogress_halfmove_count = [0]
        self.history_ep_target = [None]  # Pawns destinations used for en passant capture

        ####################
        # Info not provided by a FEN string
        ####################
        self.set_game_state(GameState.Unstarted)

        self.history_move = [None]  # The move resulting in the current Board position
        self.history_zobrist_hash = [self.get_zobrist_hash()]

        # Note: Tracking computed values avoids recomputation upon rewind/ffwd.
        # Note: No storage is needed for the non-progress states
        #   (for the 50- & 75-move rules), since they just echo
        #   the non-progress counter.
        self.history_is_check = [False]
        self.history_is_checkmate = [False]
        self.history_is_repetition_3x = [False]
        self.history_is_repetition_5x = [False]
        self.history_is_stalemate = [False]

    def init_layout(self, layout_dict: LayoutDict) -> None:
        self.pieces = [None for k in range(G.SPACE_COUNT)]
        for player in layout_dict.keys():
            for pt in layout_dict[player].keys():
                for pos in layout_dict[player][pt]:
                    self.piece_add(pos, player, pt)

    # ========================================
    # SECTION: PROPERTIES
    # ========================================
    # Some attributes are tracked in history arrays,
    # to support undo/redo, and perhaps later rewind & fastforward.
    # The current values of these attributes are accessed via properties.

    @property
    def ep_target(self) -> Npos:
        return self.history_ep_target[self.halfmove_count]

    @property
    def is_50_move_rule_triggered(self):
        return self.nonprogress_halfmove_count >= 100

    @property
    def is_75_move_rule_triggered(self):
        return self.nonprogress_halfmove_count >= 150

    @property
    def is_check(self):
        return self.history_is_check[self.halfmove_count]

    @property
    def is_checkmate(self):
        return self.history_is_checkmate[self.halfmove_count]

    @property
    def is_repetition_3x(self):
        result = False
        if self.do_check_repetition:
            result = self.history_is_repetition_3x[self.halfmove_count]
        return result

    @property
    def is_repetition_5x(self):
        result = False
        if self.do_check_repetition:
            result = self.history_is_repetition_5x[self.halfmove_count]
        return result

    @property
    def is_stalemate(self):
        return self.history_is_stalemate[self.halfmove_count]

    @property
    def last_move(self) -> Move:
        return self.history_move[self.halfmove_count]

    @property
    def nonprogress_halfmove_count(self) -> int:
        return self.history_nonprogress_halfmove_count[self.halfmove_count]

    @property
    def zobrist_hash(self) -> ZobristHash:
        return self.history_zobrist_hash[self.halfmove_count]

    # TODO: Convert to property
    def get_halfmove_count(self) -> int:
        # Don't count moves[0], which is None.
        halfmove_count = len(self.history_move) - 1

        assert self.halfmove_count == halfmove_count
        return self.halfmove_count

    # ========================================
    # SECTION: LAYOUT
    # ========================================
    # Note: This is called by get_layout_dict_str, for support of SVG creation.

    # Return the FEN Board representation, plus 5 other strings:
    #     Active color (w or b)
    #     Castling ability: Always '-' for Glinski's Hexagonal Chess
    #     En passant target space (in alg. notation), or '-'
    #     Halfmove clock
    #     Fullmove number (= floor(halfmove_count / 2))
    def get_fen(self) -> str:
        fen = self.get_fen_board()
        player = 'b' if self.cur_player == Player.Black else 'w'
        castling = '-'  # No castling in Glinski's hexagonal chess
        ep = G.npos_to_alg(self.ep_target) if self.ep_target else '-'
        nonprogress = str(self.nonprogress_halfmove_count)
        fullmove = str(1 + math.floor(self.halfmove_count / 2))
        return f'{fen} {player} {castling} {ep} {nonprogress} {fullmove}'

    def get_fen_board(self) -> str:
        result = ''
        blank_count = 0

        npos = 0
        file_count = len(G.RANK_COUNT_PER_FILE)
        for file_num in range(file_count):
            for _ in range(G.RANK_COUNT_PER_FILE[file_num]):
                cur_piece = self.get_piece_at(npos)
                npos += 1
                if cur_piece:
                    if blank_count > 0:
                        result += str(blank_count)
                        blank_count = 0
                    result += str(cur_piece)
                else:
                    blank_count += 1
            if blank_count > 0:
                result += str(blank_count)
                blank_count = 0
            if file_num < file_count - 1:
                result += '/'
        return result

    def get_king_npos(self, player: Player) -> Npos:
        for npos in range(G.SPACE_COUNT):
            piece = self.get_piece_at(npos)
            if piece and piece.player == player and piece.pt == PieceType.King:
                return npos
        raise MissingKingException(msg)

    def get_layout_dict(self) -> LayoutDict:
        layout_dict = G.get_layout_dict_empty()

        for npos in range(G.SPACE_COUNT):
            piece = self.get_piece_at(npos)
            if not piece:
                continue
            player = piece.player
            pt = piece.pt
            layout_dict[player][pt].append(G.npos_to_pos(npos))
        return layout_dict

    def get_piece_at(self, npos: Npos) -> Piece:
        return self.pieces[npos]

    def get_pieces_at_file(self, f: str,
            player:Player=None, pt:PieceType=None) -> Iterable[Piece]:
        result = []
        for npos in BITBOARD_FILES[G.FILE_CHAR_TO_HEX0[f]]:
            piece = self.get_piece_at(npos)
            if piece:
                if ((player is None or piece.player == player)
                        and (pt is None or piece.pt == pt)):
                    result.append(piece)
        return result

    def get_pieces_at_rank(self, r: int,
            player:Player=None, pt:PieceType=None) -> Iterable[Piece]:
        result = []
        for npos in G.BITBOARD_RANKS[r - 1].search(1):
            piece = self.get_piece_at(npos)
            if piece:
                if ((player is None or piece.player == player)
                        and (pt is None or piece.pt == pt)):
                    result.append(piece)
        return result

    def get_player_at(self, npos: Npos) -> Player:
        return self.pieces[npos].player

    def get_pt_at(self, npos: Npos) -> PieceType:
        return self.pieces[npos].pt

    # For each piece on the Board, there is a corresponding unique triple:
    #   (Board position ID, player ID, piece_type ID).
    # That is used to look up a value in the ZobristTable that
    # corresponds to that triplet.
    #   * The Board position ID (npos) selects a plane.
    #   * The Player value (p_val) selects a row within that plane.
    #   * The PieceType value (p_val) selects a column within that plane.
    # All such values are XORed together to form the final result.
    def get_zobrist_hash(self) -> ZobristHash:
        result = 0
        for npos in range(G.SPACE_COUNT):
            piece = self.get_piece_at(npos)
            if piece is not None:
                p_val = piece.player.value
                pt_val = piece.pt.value
                zobrist_index = (npos * PLAYER_COUNT * PIECE_TYPE_COUNT
                    + p_val * PIECE_TYPE_COUNT + pt_val)
                result ^= ZOBRIST_TABLE[zobrist_index]
        return result

    # --------------------

    def is_empty(self, npos: Npos):
        return self.get_piece_at(npos) is None

    def is_ep_target(self, npos: Npos):
        return npos == self.ep_target

    def is_in_court_zone(self, npos: Npos, player:Player=None):
        if player is None:
            player = self.cur_player
        if player == Player.Black:
            result = bool(BB_COURT_BLACK[npos])
        else:
            result = bool(BB_COURT_WHITE[npos])
        return result

    def is_in_pawn_ep_target_zone(self, npos: Npos, player:Player=None):
        if player is None:
            player = self.cur_player
        if player == Player.Black:
            result = bool(BB_PAWN_EP_TARGET_BLACK[npos])
        else:
            result = bool(BB_PAWN_EP_TARGET_WHITE[npos])
        return result

    def is_in_pawn_home_zone(self, npos: Npos, player:Player=None):
        if player is None:
            player = self.cur_player
        if player == Player.Black:
            result = bool(BB_PAWN_HOME_BLACK[npos])
        else:
            result = bool(BB_PAWN_HOME_WHITE[npos])
        return result

    def is_in_pawn_promo_zone(self, npos: Npos, player:Player=None):
        if player is None:
            player = self.cur_player
        if player == Player.Black:
            result = bool(BB_PAWN_PROMO_BLACK[npos])
        else:
            result = bool(BB_PAWN_PROMO_WHITE[npos])
        return result

    # --------------------

    def piece_add(self, pos: HexPos, player: Player, pt: PieceType) -> None:
        npos = G.pos_to_npos(pos)
        self.piece_add_at(npos, player, pt)

    def piece_add_at(self, npos: Npos, player: Player, pt: PieceType) -> None:
        self.pieces[npos] = Piece(player, pt)

    def piece_move(self, fr_npos: Npos, to_npos: Npos) -> None:
        assert self.is_empty(to_npos)
        fr_piece = self.get_piece_at(fr_npos)
        self.piece_add_at(to_npos, fr_piece.player, fr_piece.pt)
        self.piece_remove(fr_npos)

    def piece_remove(self, npos: Npos) -> None:
        self.pieces[npos] = None

    def piece_set_pt(self, npos: Npos, pt: PieceType) -> None:
        player = self.get_player_at(npos)
        self.piece_remove(npos)
        self.piece_add_at(npos, player, pt)

    # ========================================
    # SECTION: PIECE MOVEMENT
    # ========================================
    def get_leap_pawn_adv(self, npos: Npos) -> Npos:
        if self.cur_player == Player.Black:
            result = G.LEAP_PAWN_ADV_BLACK[npos]
        else:
            result = G.LEAP_PAWN_ADV_WHITE[npos]
        return result

    def get_leap_pawn_capt(self, npos: Npos) -> List[Npos]:
        if self.cur_player == Player.Black:
            result = G.LEAP_PAWN_CAPT_BLACK[npos]
        else:
            result = G.LEAP_PAWN_CAPT_WHITE[npos]
        return result

    def get_leap_pawn_hop(self, npos: Npos) -> Npos:
        if self.cur_player == Player.Black:
            result = G.LEAP_PAWN_HOP_BLACK[npos]
        else:
            result = G.LEAP_PAWN_HOP_WHITE[npos]
        return result

    def get_moves_legal(self) -> Iterable[Move]:
        result = []
        for move in self.get_moves_pseudolegal():
            player = self.cur_player
            self.move_make(move)
            if not self.is_king_attacked():
                result.append(move)
            self.move_undo()
        return result

    # Move specifications (in text, or in a MoveSpec object) can be:
    #   * unambiguous (e.g., Nb2e4)
    #   * ambiguous without board context (e.g., dxe5)
    # If a move is written without a PieceType or starting position
    #   (e.g., b5), and both a Pawn and another PieceType could have
    #   moved there, we should probably give priority to the Pawn.
    # Possible alternate approach: Find all legal moves, and( apply filter.
    # Note: The "move_text" arg is not needed, but can be helpful for debugging.
    def get_moves_matching(self, ms: MoveSpec, move_text) -> Iterable[Move]:  # pylint: disable=unused-argument
        moves = []

        if ms.fr_file and ms.fr_rank and ms.to_file and ms.to_rank:
            # TODO: Find fr_npos & to_npos more efficiently.
            fr_npos = G.alg_to_npos(ms.fr_file + str(ms.fr_rank))
            to_npos = G.alg_to_npos(ms.to_file + str(ms.to_rank))
            move = Move(fr_npos, to_npos, ms.promotion_pt)
            move.pt = ms.pt
            move.is_capture = ms.is_capture
            move.is_check = ms.checkness_str and ms.checkness_str == '+'
            move.is_checkmate = ms.checkness_str and ms.checkness_str == '#'
            if ms.promotion_pt:
                move.promotion_pt = ms.promotion_pt
            move.is_checkmate = ms.checkness_str and ms.checkness_str == '#'
            if move.pt == PieceType.Pawn and move.to_npos == self.ep_target:
                to_file_char = G.npos_to_file_char(to_npos)
                fr_file_char = G.npos_to_file_char(fr_npos)
                if to_file_char != fr_file_char:
                    move.ep_target = self.ep_target
            # TODO: move_eval
            return [move]
        if ms.to_file and ms.to_rank:
            # We know the moving Piece's destination
            to_npos = G.alg_to_npos(ms.to_file + str(ms.to_rank))
            if ms.promotion_pt:
                assert self.is_in_pawn_promo_zone(to_npos)
            moves = self.get_moves_to(to_npos)
            if not moves:
                return []

            # Filter on PieceType. The Piece on the Board matches the spec.
            moves = [move for move in moves
                    if (self.get_pt_at(move.fr_npos) == ms.pt)
                    or (ms.pt is None
                        and self.get_pt_at(move.fr_npos) == PieceType.Pawn)]
            if not moves:
                return []

            if ms.is_capture:
                opponent = self.cur_player.opponent()
                moves = [move for move in moves
                        if ((self.get_piece_at(move.to_npos)
                            and self.get_player_at(move.to_npos) == opponent)
                            or (move.to_npos == self.ep_target
                                and self.is_empty(self.ep_target)))
                            ]
                if not moves:
                    return []

            if ms.fr_file:
                moves = [move for move in moves
                        if G.npos_to_file_char(move.fr_npos) == ms.fr_file]
                if not moves:
                    return []

            if ms.fr_rank:
                moves = [move for move in moves
                        if G.npos_to_rank(move.fr_npos) == ms.fr_rank]
                if not moves:
                    return []

            if ms.promotion_pt:
                moves = [move for move in moves
                        if move.promotion_pt == ms.promotion_pt]

            return moves

        # TODO: Consider expanding to handle capture by non-Pawn pieces
        if (ms.pt is None and ms.fr_file and ms.is_capture and ms.to_file
                and (not ms.fr_rank and not ms.to_rank)):
            bb_file = BITBOARD_FILES[G.FILE_CHAR_TO_HEX0[ms.fr_file] + 5]
            for fr_npos in bb_file.search(bitarray('1')):
                if self.is_empty(fr_npos):
                    continue
                fr_piece = self.get_piece_at(fr_npos)
                if (self.get_player_at(fr_npos) != self.cur_player
                        or self.get_pt_at(fr_npos) != PieceType.Pawn):
                    continue
                if self.is_in_pawn_promo_zone(fr_npos):
                    assert False  # TODO: There shouldn't be a Pawn in the last rank.

                for to_npos in self.get_leap_pawn_capt(fr_npos):
                    if G.npos_to_file_char(to_npos) != ms.to_file:
                        continue
                    move = Move(fr_npos, to_npos, ms.promotion_pt or None)
                    move.pt = PieceType.Pawn
                    move.is_capture = True
                    move.is_check = ms.checkness_str and ms.checkness_str == '+'
                    move.is_checkmate = ms.checkness_str and ms.checkness_str == '#'
                    move.ep_target = to_npos if self.ep_target == to_npos else None
                    # TODO: Set move_eval
                    moves.append(move)
            return moves
        raise NotImplementedError('board.get_moves_matching(). Move pattern not recognized')

    def get_moves_pseudolegal(self) -> Iterable[Move]:
        moves = []
        for npos in range(G.SPACE_COUNT):
            piece = self.get_piece_at(npos)
            if piece and piece.player == self.cur_player:
                moves.extend(self.get_moves_pseudolegal_from(npos))
        return moves

    def get_moves_pseudolegal_from(self, npos: Npos) -> Iterable[Move]:
        piece = self.get_piece_at(npos)
        if piece is None or piece.player != self.cur_player:
            return []
        pt = piece.pt
        if pt in [PieceType.King, PieceType.Knight]:
            moves = self.get_moves_pseudolegal_leaper(npos, pt)
        elif PieceType.is_slider_type(pt):
            moves = self.get_moves_pseudolegal_slider(npos, pt)
        else:  # pt == Piece.Pawn
            moves = self.get_moves_pseudolegal_pawn(npos)
        return moves

    def get_moves_pseudolegal_leaper(self, npos: Npos, pt: PieceType) -> Iterator[Move]:
        if pt == PieceType.King:
            leaps_npos = G.LEAPS_KING[npos]
        else:
            assert pt == PieceType.Knight
            leaps_npos = G.LEAPS_KNIGHT[npos]

        for to_npos in leaps_npos:
            to_piece = self.get_piece_at(to_npos)
            if to_piece is None:
                yield Move(npos, to_npos, None)
            elif to_piece.player == self.cur_player.opponent():
                move = Move(npos, to_npos, None)
                yield move

    # TODO: Allow for selection of promotion_pt on Pawn promotion
    def get_moves_pseudolegal_pawn(self, npos: Npos) -> Iterator[Move]:
        is_verbose = (npos == 11
                and self.get_player_at(npos) == Player.Black
                and self.get_pt_at(npos) == PieceType.Pawn)

        fwd1_npos = self.get_leap_pawn_adv(npos)
        fwd1_piece = self.get_piece_at(fwd1_npos)
        if not fwd1_piece:  # ADV1
            if self.is_in_pawn_promo_zone(fwd1_npos):
                for promo_pt in PROMO_PTS:
                    yield Move(npos, fwd1_npos, promo_pt)  # ADV1 w/ PROMOTION
            else:
                yield Move(npos, fwd1_npos, None)  # ADV1 w/o promotion
            if self.is_in_pawn_home_zone(npos):
                fwd2_npos = self.get_leap_pawn_hop(npos)
                fwd2_piece = self.get_piece_at(fwd2_npos)
                if not fwd2_piece:  # ADV2
                    yield Move(npos, fwd2_npos, None)  # ADV2 w/o promotion

        for capt_npos in self.get_leap_pawn_capt(npos):
            if capt_npos == self.ep_target:
                move = Move(npos, capt_npos, None)  # E.P. CAPTURE
                move.capture_pt = PieceType.Pawn
                move.ep_target = self.ep_target
                yield move
            else:
                capt_piece = self.get_piece_at(capt_npos)
                if capt_piece and capt_piece.player == self.cur_player.opponent():
                    if self.is_in_pawn_promo_zone(capt_npos):
                        for promo_pt in PROMO_PTS:
                            move = Move(npos, capt_npos, promo_pt)  # Capture with PROMOTION
                            move.capture_pt = capt_piece.pt
                            yield move
                    else:
                        move = Move(npos, capt_npos, None)  # Capture w/o promotion
                        move.capture_pt = capt_piece.pt
                        yield move

    def get_moves_pseudolegal_slider(self, npos: Npos, pt: PieceType) -> Iterator[Move]:
        rays = G.get_rays(npos, pt)
        for ray in rays:
            for to_npos in ray:
                if self.is_empty(to_npos):
                    yield Move(npos, to_npos)
                    continue
                else:
                    if self.get_player_at(to_npos) == self.cur_player.opponent():
                        # Capture opponent's piece
                        move = Move(npos, to_npos)
                        move.capture_pt = self.get_pt_at(to_npos)
                        yield move
                break # Can't slide past piece

    # TODO: Check slider moves being blocked
    # TODO: Check for move legality
    def get_moves_to(self, to_npos: Npos) -> Iterable[Move]:
        result = []

        # TODO: Greatly improve efficiency with move selective checking.
        for fr_npos in range(G.SPACE_COUNT):
            if self.is_empty(fr_npos):
                continue
            if self.get_player_at(fr_npos) != self.cur_player:
                continue
            moves = self.get_moves_pseudolegal_from(fr_npos)
            for move in moves:
                if move.to_npos == to_npos:
                    move.pt = self.get_pt_at(fr_npos)
                    result.append(move)
        return result

    # This is used to obtain the location of a Pawn being
    # captured by en passant, given the e.p. target space.
    def get_vec_pawn_reverse(self) -> HexVec:
        if self.cur_player == Player.Black:
            result = G.VECS_PAWN_ADV_WHITE
        else:
            result = G.VECS_PAWN_ADV_BLACK
        return result

    # --------------------

    # Called by is_condition_check() / is_condition_checkmate()
    # When player=None, player=self.cur_player is assumed.
    # In theory, player=self.cur_player.opponent() could be used
    #   to detect the error condition in which the opponent of
    #   the player moving is already in 'check'.
    # See FIDE rule 3.9.1: Psuedolegal attacks suffice to bring mate.
    def is_king_attacked(self):
        player = self.cur_player
        opponent = player.opponent()
        king_npos = self.get_king_npos(opponent)
        for attacker_npos in range(G.SPACE_COUNT):
            attacker_piece = self.pieces[attacker_npos]
            if attacker_piece and attacker_piece.player == player:
                moves = self.get_moves_pseudolegal_from(attacker_npos)
                attacks = [attack for attack in moves
                            if attack.to_npos == king_npos]
                if attacks:
                    return True
        return False

    # Check whether cur_player's King is being attacked.
    # When do_check_pseudolegal=False, pseudolegality is presumed.
    # Consider adding player=self.cur_player param for sanity check
    #     to determine whether last move left own King attacked.
    def is_move_legal(self, m: Move, do_check_pseudolegality=False):
        if do_check_pseudolegality:
            pseudolegal = self.is_move_pseudolegal(m)
            if not pseudolegal:
                return False
        self.move_make(m)
        is_legal = not self.is_king_attacked()
        self.move_undo(m)
        return is_legal

    def is_move_pseudolegal(self, m: Move):
        raise NotImplementedError('board.is_move_pseudolegal()')

    # --------------------

    # Note: This method does not (currently) perform a check for move legality.
    # Note: This board sets board_state. It is up to the caller to check this
    #   value to see if the game is over (e.g., Checkmate, Draw, Stalemate).
    #   * game.play() will act on this by ending the game.
    #   * another caller (e.g., move search) might handle it differently.
    # TODO: Add an option "do_force" to allow an illegal move.
    def move_make(self, move) -> None:
        # Phase 0:
        assert self.get_game_state() in [GameState.Unstarted, GameState.InPlay]
        if self.get_game_state() == GameState.Unstarted:
            self.set_game_state(GameState.InPlay)

        # Phase 1: Capture.
        #
        if move.ep_target:
            move.capture_pt = PieceType.Pawn
            ep_target_pos = G.npos_to_pos(move.ep_target)
            captured_pawn_pos = ep_target_pos + self.get_vec_pawn_reverse()
            captured_pawn_npos = G.pos_to_npos(captured_pawn_pos)
            self.piece_remove(captured_pawn_npos)
        else:
            to_piece = self.pieces[move.to_npos]
            if not self.is_empty(move.to_npos):
                move.capture_pt = self.get_pt_at(move.to_npos)
                self.piece_remove(move.to_npos)

        # Phase 2: Move piece
        #
        if (self.get_pt_at(move.fr_npos) == PieceType.Pawn
                and self.is_in_pawn_home_zone(move.fr_npos)
                and move.to_npos == self.get_leap_pawn_hop(move.fr_npos)):
            next_ep_target = self.get_leap_pawn_adv(move.fr_npos)
        else:
            next_ep_target = None

        self.piece_move(move.fr_npos, move.to_npos)

        # Phase 3: Pawn promotion.
        #
        # TODO: Implement Pawn promotion
        if move.promotion_pt:
            assert move.pt == PieceType.Pawn
            assert self.is_in_pawn_promo_zone(move.to_npos)
            self.piece_set_pt(move.to_npos, move.promotion_pt)

        # Phase 4: Check for end of Game

        # TODO: Uncomment. Method compute_board_state() is in progress.
        TODO_is_compute_board_state_complete = False
        if TODO_is_compute_board_state_complete:
            board_state = self.compute_board_state()
        else:
            board_state = BoardState.Normal

        if board_state == BoardState.Check:
            self.notify_player(self.cur_player.opponent(), 'Check')
        next_zobrist_hash = self.get_zobrist_hash()

        if board_state == BoardState.Checkmate:
            if self.cur_player == Player.Black:
                self.set_game_state(GameState.WinBlack)
            else:
                self.set_game_state(GameState.WinWhite)
        elif board_state == BoardState.Stalemate:
            if self.cur_player == Player.Black:
                self.set_game_state(GameState.WinBlackStalemate)
            else:
                self.set_game_state(GameState.WinWhiteStalemate)
        is_pending_draw = (
                # Check for 75-moves of non-progress and/or 5x board repetition
                (not move.is_progress() and self.nonprogress_halfmove_count == 149)
                or
                (self.do_check_repetition
                    and (len([z for z in self.history_zobrist_hash
                        if z == next_zobrist_hash]) == 4))
                )
        if board_state in [BoardState.Checkmate, BoardState.Stalemate] or is_pending_draw:
            raise NotImplementedError('board: Termination of Game')

        # Phase 5: Update counters & history
        #
        self.history_zobrist_hash.append(next_zobrist_hash)
        zobrist_counter = Counter(self.history_zobrist_hash)
        max_reps = max(zobrist_counter.values())
        next_is_board_repetition_3x = max_reps >= 3
        next_is_board_repetition_5x = max_reps >= 5
        next_nonprogress_count = (0 if move.is_progress()
                else self.history_nonprogress_halfmove_count[-1] + 1)

        # Already set above: history_zobirst_hash
        self.history_ep_target.append(next_ep_target)
        self.history_is_check.append(board_state == BoardState.Check)
        self.history_is_checkmate.append(board_state == BoardState.Checkmate)
        self.history_is_repetition_3x.append(next_is_board_repetition_3x)
        self.history_is_repetition_5x.append(next_is_board_repetition_5x)
        self.history_is_stalemate.append(board_state == BoardState.Stalemate)
        self.history_move.append(move)
        self.history_nonprogress_halfmove_count.append(next_nonprogress_count)

        # Phase 6: Move to the next halfmove & Player
        #
        self.halfmove_count += 1
        self.cur_player = self.cur_player.opponent()
        self.notify_player(self.cur_player, 'Your move')

    def move_undo(self) -> None:
        assert self.get_game_state() != GameState.Unstarted
        move = self.history_move[-1]

        # Restore Game state
        self.set_game_state(GameState.InPlay)

        # Restore piece positions
        mover = self.cur_player.opponent()
        opponent = self.cur_player

        assert self.is_empty(move.fr_npos)
        self.piece_move(move.to_npos, move.fr_npos)
        assert not self.is_empty(move.fr_npos)

        # Restore captured piece, if any
        if move.capture_pt:
            if move.ep_target:
                ep_targ = self.history_ep_target[-2]
                self.piece_add(ep_targ, opponent, PieceType.Pawn)
            else:
                self.piece_add(move.to_npos, opponent, move.pt)

        # Remove last value from each of the history stacks
        self.history_ep_target.pop()
        self.history_move.pop()
        self.history_nonprogress_halfmove_count.pop()
        self.history_zobrist_hash.pop()

        self.history_is_check.pop()
        self.history_is_checkmate.pop()
        self.history_is_repetition_3x.pop()
        self.history_is_repetition_5x.pop()
        self.history_is_stalemate.pop()

        self.halfmove_count -= 1
        assert len(self.history_ep_target) == self.halfmove_count + 1
        assert len(self.history_move) == self.halfmove_count + 1
        assert len(self.history_nonprogress_halfmove_count) == self.halfmove_count + 1
        assert len(self.history_zobrist_hash) == self.halfmove_count + 1
        assert len(self.history_is_check) == self.halfmove_count + 1
        assert len(self.history_is_checkmate) == self.halfmove_count + 1
        assert len(self.history_is_repetition_3x) == self.halfmove_count + 1
        assert len(self.history_is_repetition_5x) == self.halfmove_count + 1
        assert len(self.history_is_stalemate) == self.halfmove_count + 1
        self.cur_player = self.cur_player.opponent()

    def moves_make(self, moves) -> None:
        raise NotImplementedError('board.moves_make()')

    def moves_undo(self, moves) -> None:
        raise NotImplementedError('board.moves_undo()')

    # ========================================
    # SECTION: DETECT ENDGAME
    # ========================================

    def compute_board_state(self) -> BoardState:
        moves = self.get_moves_pseudolegal()
        is_king_attacked = self.is_king_attacked()
        if is_king_attacked:
            is_escapable = False
            for protect_move in self.get_moves_pseudolegal():
                self.move_make(protect_move)
                if not self.is_king_attacked():
                    is_escapable = True
                self.make_undo()
                if is_escapable:
                    break
            if is_escapable:
                result = BoardState.Check
            else:
                result = BoardState.Checkmate
        else:
            if len(moves) == 0:
                result = BoardState.Stalemate
            else:
                result = BoardState.Normal
        return result

    # To simplify testing of 50-move and 75-move rules
    def disable_check_repetition(self) -> None:
        self.do_check_repetition = False

    def get_board_state(self) -> BoardState:
        return self.board_state

    def get_game_state(self) -> GameState:
        return self.game_state

    def get_max_repetition_count(self) -> int:
        return max(Counter(self.history_zobrist_hash).values())

    def is_condition_dead_position(self):
        raise NotImplementedError('board.is_condition_dead_position()')

    def is_condition_insufficient_material(self):
        def get_pt_histo(player, Player):
            pt_histo = [0] * 6
            for npos in range(G.SPACE_COUNT):
                piece = self.pieces[npos]
                if piece:
                    if piece.player == player:
                        pt_histo[piece.pt.value] += 1

        # Turns a vector of length-6 integers (digits 0-9) into an int.
        # Example: [1, 1, 2, 3, 1, 6] -> 112316
        # Since the first digit of pt_histo_* represent the count of Kings,
        # there should always be a leading '1'.
        def pt_histo_to_pt_sig(vec: List[int]):
            sig = 0
            for k in range(6):
                sig += vec[k] * 10**(5-k)

        pt_histo_black = get_pt_histo(Player.Black)
        pt_sig_black = histo_to_sig(pt_histo_black)

        pt_histo_white = get_pt_histo(Player.White)
        pt_sig_white = histo_to_sig(pt_histo_white)

        # K vs K
        if pt_sig_black == 100_000 and pt_sig_white == 100_000:
            return True

        # KB vs K
        if ((pt_sig_black == 100_100 and pt_sig_white == 100_000)
                or (pt_sig_black == 100_000 and pt_sig_white == 100_100)):
            return True

        # KN vs K
        if ((pt_sig_black == 100_010 and pt_sig_white == 100_000)
                or (pt_sig_black == 100_000 and pt_sig_white == 100_010)):
            return True

        # KNN vs K
        if ((pt_sig_black == 100_020 and pt_sig_white == 100_000)
                or (pt_sig_black == 100_000 and pt_sig_white == 100_020)):
            return True

        # KB vs K
        if ((pt_sig_black == 100_100 and pt_sig_white == 100_000)
                or (pt_sig_black == 100_000 and pt_sig_white == 100_100)):
            return True

        # KBB vs K
        if ((pt_sig_black == 100_200 and pt_sig_white == 100_000)
                or (pt_sig_black == 100_000 and pt_sig_white == 100_200)):
            return True

    def set_board_state(self, board_state) -> None:
        self.board_state = board_state

    def set_game_state(self, game_state) -> None:
        self.game_state = game_state

    # ========================================
    # SECTION: DETECT ERRORS
    # ========================================
    def get_board_errors(self) -> BoardErrorFlags:
        result = 0
        layout_dict = self.get_layout_dict()

        if (len(layout_dict[Player.Black][PieceType.King]) > 1
                or len(layout_dict[Player.White][PieceType.King]) > 1):
            result |= BoardErrorFlags.ExcessKings

        if (len(layout_dict[Player.Black][PieceType.Pawn]) > 9
                or len(layout_dict[Player.White][PieceType.Pawn]) > 9):
            result |= BoardErrorFlags.ExcessPawns

        if (sum([len(ps) for ps in layout_dict[Player.Black].values()]) > 18
                or sum([len(ps) for ps in layout_dict[Player.White].values()]) > 18):
            result |= BoardErrorFlags.ExcessPieces

        if self.ep_target and not self.is_in_pawn_ep_target_zone(self.ep_target):
            result |= BoardErrorFlags.InvalidEpTarget

        if (len(layout_dict[Player.Black][PieceType.King]) == 0
                or len(layout_dict[Player.White][PieceType.King]) == 0):
            result |= BoardErrorFlags.MissingKing

        if (any([self.is_in_court_zone(G.pos_to_npos(p), Player.Black)
                for p in layout_dict[Player.Black][PieceType.Pawn]])
            or any([self.is_in_court_zone(G.pos_to_npos(p), Player.Black)
                for p in layout_dict[Player.White][PieceType.Pawn]])):
            result |= BoardErrorFlags.PawnInCourt

        if (any([self.is_in_pawn_promo_zone(G.pos_to_npos(p), Player.Black)
                for p in layout_dict[Player.Black][PieceType.Pawn]])
            or any([self.is_in_pawn_promo_zone(G.pos_to_npos(p), Player.White)
                for p in layout_dict[Player.White][PieceType.Pawn]])):
            result |= BoardErrorFlags.PawnOnBackRank
        return result

    # ========================================
    # SECTION: PLAYER NOTIFICATION
    # ========================================
    # TODO: Implement
    # Notification should be done by Game & Player/Controller
    def notify_player(self, player: Player, msg: str):
        pass
        # print(f'Attention {player}: {msg}')

    # ========================================
    # SECTION: PUZZLE SUPPORT
    # ========================================
    def find_mates_in_1(self) -> Iterable[Move]:
        moves = self.get_moves_legal()
        result = []
        for move in moves:
            self.move_make(move)
            if self.is_checkmate():
                result.append(move)
            self.move_undo(move)
        return result

    # Assume the next player to move is White
    # Returns a tree structure of moves, with depth 3:
    #   mates_in_2[m_p][m_opp][
    #   A first move, followed by a series of moves leading to checkmate.
    def find_mates_in_2(self)-> Dict:
        mates_in_2 = {}
        moves_p = self.get_moves_legal()
        for m_p in moves_p:
            inevitable_mates = find_mates_in_2_starting_with(m_p)
            if inevitable_mates:
                mates_in_2[m_p] = inevitable_mates
        return mates_in_2

    # p:   The Player who makes move m_p.
    # opp: The opponent of Player p. Player opp makes move m_opp.
    #
    def find_mates_in_2_starting_with(self, m_p) -> Dict:
        inevitable_mates = {}
        self.move_make(m_p)
        moves_opp = self.get_moves_legal()
        for m_opp in moves_opp:
            self.move_make(m_opp)
            if self.get_game_state() == GameState.InPlay():
                is_mate_avoidable = True
                self.move_undo(m_p)
                break
            mates_p = [m2_p for m2_p in self.get_moves_legal()
                    if self.is_checkmate(m2_p)]
            if len(mates_p) == 0:
                is_mate_avoidable = True
                self.move_undo(m_opp)
                break
            if not m_p in inevitable_mates:
                inevitable_mates[m_opp] = mates_p
                self.move_undo(m_opp)
        if is_mate_avoidable:
            result = {}
        else:
            result = inevitable_mates
        return result

    # ========================================
    # SECTION: VISUAL REPRESENTATION
    # ========================================

    # --------------------
    # Print methods
    # --------------------
    def get_print_str(self, indent_board=8,
            indent_incr=3, item_width=6, do_use_unicode=False) -> None:
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

        def empty_space(npos: Npos) -> str:
            bullet = '\u2022'
            center_dot = '\xB7'
            # em_dash = '\u2014'
            # en_dash = '\u2013'

            color = G.get_board_color(npos)
            if color == BoardColor.Light:
                return center_dot
            if color == BoardColor.Medium:
                return '-'
            else:  # color == BoardColor.Dark:
                return bullet

        def row_indent_size(row_num) -> int:
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
                npos = int(item)
                piece = self.pieces[npos]
                if do_use_unicode:
                    txt = (pt.to_unicode(player.value)
                            if piece else empty_space(npos))
                else:
                    txt = str(piece) if piece else empty_space(npos)
                row_str += str(txt.ljust(item_width))
            result_rows.append(row_str.rstrip())  # End of row
        return '\n'.join(result_rows)

    def print(self, heading=None, indent_board=8,
            indent_incr=3, item_width=6,
            do_use_unicode=False, do_print_info=True) -> None:
        text = self.get_print_str(indent_board, indent_incr, item_width)
        if heading:
            print(heading + ':')
        print(text)
        if do_print_info:
            self.print_info()
        print()

    def print_ascii(self, heading=None, indent_board=8,
            indent_incr=3, item_width=6, do_print_info=True) -> None:
        self.print(heading, indent_board,
                indent_incr, item_width,
                False, do_print_info)

    def print_info(self) -> None:
        ep_tgt = self.ep_target
        ep_str = (f'{G.npos_to_alg(ep_tgt) if ep_tgt else "None"}')
        opp_name = self.cur_player.opponent().name
        rep_count = f'{max(Counter(self.history_zobrist_hash).values())}'
        print(f'1/2-moves={self.halfmove_count}. '
                + f'{opp_name}\'s last move: {self.last_move}. '
                + f'{self.cur_player.name}\'s turn. '
                + f'(Non-progress={self.nonprogress_halfmove_count}, '
                + f'Rep-count={rep_count}, '
                + f'EP-tgt={ep_str})')

    def print_unicode(self, heading=None, indent_board=8,
            indent_incr=3, item_width=6, do_print_info=True) -> None:
        self.print(heading, indent_board,
                indent_incr, item_width,
                True, do_print_info)

    # --------------------
    # SVG methods
    # --------------------
    # This returns a string suitable for interpolation
    # into an SVG template file, supporting SVG output of Boards.
    # This is called by svg_get_str().
    def svg_get_layout_dict_str(self, fr_npos=None, to_npos=None,
            king_check_npos=None, king_checkmate_npos=None) -> str:
        SVG_PLAYER_KEYS = { Player.Black: 'black', Player.White: 'white' }
        layout_dict = self.get_layout_dict()
        result = '\tLAYOUT = {\n'
        for player in PLAYERS:
            result += '\t\t"' + SVG_PLAYER_KEYS[player] + '": {\n'
            for pt in PIECE_TYPES:
                pos_str = ', '.join([G.pos_to_alg(pos).upper()
                    for pos in layout_dict[player][pt]])
                result += f'\t\t\t"{pt}": [{pos_str}],\n'
            result += '\t\t},\n'

        from_coords_str = f'{G.npos_to_alg(fr_npos).upper() if fr_npos else "null"}'
        to_coords_str = f'{G.npos_to_alg(to_npos).upper() if to_npos else "null"}'
        check_str = f'{G.npos_to_alg(king_check_npos).upper() if king_check_npos else "null"}'
        checkmate_str = f'{G.npos_to_alg(king_checkmate_npos).upper() if king_checkmate_npos else "null"}'

        result += '\t}\n'
        result += f'\tFROM_COORDS = {from_coords_str}\n'
        result += f'\tTO_COORDS = {to_coords_str}\n'
        result += '\n'
        result += f'\tKING_CHECK_COORDS = {check_str}\n'
        result += f'\tKING_CHECKMATE_COORDS = {checkmate_str}\n'
        return result

    # This interpolates the output of svg_get_layout_dict_str() into
    # an SVG template file to create the content of an SVG file
    # that can be stored to disk and used standalone, or in a
    # slideshow or animation.
    # Note: The selenium package can open "data URLs", so this SVG
    #   content can be used even without ever being saved to disk.
    def svg_get_str(self, fr_npos:Npos=None, to_npos:Npos=None,
            king_check_npos:Npos=None, king_checkmate_npos=None) -> str:
        glinski_home = os.getenv('GLINSKI_HOME')
        template_svg_dir = '/assets/'
        svg_fname = 'glinski_game.svg'
        svg_path = glinski_home + template_svg_dir + svg_fname

        is_echoing = True
        result = ''
        layout_str = self.svg_get_layout_dict_str(fr_npos, to_npos)
        with open(svg_path, 'r') as f:
            svg_lines = f.readlines()
        for svg_line in svg_lines:
            if 'END_LAYOUT' in svg_line:
                result += layout_str
                is_echoing = True
            if is_echoing:
                result += svg_line
            if 'BEGIN_LAYOUT' in svg_line:
                is_echoing = False
        return result

    # Write an SVG file of the form
    #   <gamename>_<halfmovecount><suffix>.svg
    # For example, foo_037b.svg
    # The presence of the halfmove count supports recording
    #   of images of an entire game.
    # The suffix supports the addition of additional frames, which
    #   could be helpful in adding frames to a slideshow or animation.
    def svg_write(self, out_dir:str=None,
            game_name:str=None, suffix:str=None,
            fr_npos:Npos=None, to_npos:Npos=None,
            king_check_npos:Npos=None, king_checkmate_npos:Npos=None) -> None:
        if out_dir is None:
            glinski_home = os.getenv('GLINSKI_HOME')
            out_dir = glinski_home + '/assets/custom/'
        if game_name is None:
            game_name = 'glinski'
        if suffix is None:
            suffix = ''
        out_fname = f'{game_name}_{self.halfmove_count:03}{suffix}.svg'
        out_path = out_dir + out_fname
        svg_content = self.svg_get_str(fr_npos, to_npos,
                king_check_npos, king_checkmate_npos)
        with open(out_path, 'w') as f:
            f.write(svg_content)

