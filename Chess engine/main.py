# A fully playable chess game with a start menu, an AI opponent, and a stats sidebar.
# This version includes fixes for the screen width, the accuracy of captured pieces,
# and consolidates all code into a single file to resolve the import error.
# Features: legal move validation, captures, check, checkmate, stalemate, castling, en passant, promotion.
# The AI uses a simple Minimax algorithm with a depth of 2.

from typing import List, Tuple, Dict, Optional, Any
import pygame
import os
import array
import random
import sys
import time

pygame.init()

# --- CONSTANTS ---
# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
# Board dimensions
BOARD_SIZE_PX = 600
BOARD_SIZE = 8
SQUARE_SIZE = BOARD_SIZE_PX // BOARD_SIZE
FPS = 60

# Colors
WHITE = (238, 238, 210)
BLACK = (118, 150, 86)
BACKGROUND_COLOR = (49, 46, 43)
HIGHLIGHT = (255, 255, 0, 150)
MOVE_HIGHLIGHT = (255, 255, 0, 150)
CHECK_RED = (255, 0, 0, 150)
COORD_COLOR = (200, 200, 200)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (150, 150, 150)
BAR_WHITE = (255, 255, 255)
BAR_BLACK = (0, 0, 0)
PIECE_VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, 30)
BOLD_FONT = pygame.font.Font(None, 40)
LARGE_FONT = pygame.font.Font(None, 80)
PIECE_FONT = pygame.font.Font(None, SQUARE_SIZE)
# Assuming you have a Lessons list defined elsewhere
LESSONS: list = []

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Engine")
clock = pygame.time.Clock()
FPS = 60


# Function to convert algebraic notation to position (row, col)
def algebraic_to_pos(algebraic: str) -> Tuple[int, int]:
    col = ord(algebraic[0].lower()) - ord('a') + 1
    row = int(algebraic[1])
    return (row, col)

# --- BOARD CLASS ---
class Board:
    def __init__(self):
        self.array: List[List[str]] = [[" " for _ in range(8)] for _ in range(8)]

    def return_array(self) -> List[List[str]]:
        return self.array

    def put_piece(self, r: int, c: int, piece: str):
        if not (1 <= r <= 8 and 1 <= c <= 8):
            raise ValueError("Position out of bounds")
        self.array[r-1][c-1] = piece

    def get_piece(self, r: int, c: int) -> str:
        if not (1 <= r <= 8 and 1 <= c <= 8):
            return " "
        return self.array[r-1][c-1]
        
    def copy(self) -> "Board":
        new_board = Board()
        new_board.array = [row[:] for row in self.array]
        return new_board

# --- HELPERS ---
FILE_TO_COL = {c: i+1 for i, c in enumerate("abcdefgh")}
COL_TO_FILE = {v: k for k, v in FILE_TO_COL.items()}
Position = Tuple[int, int]

def in_bounds(r: int, c: int) -> bool:
    return 1 <= r <= 8 and 1 <= c <= 8

def algebraic_to_pos_helper(s: str) -> Position:
    if len(s) != 2 or s[0] not in FILE_TO_COL or not s[1].isdigit():
        raise ValueError("Invalid square: " + s)
    col = FILE_TO_COL[s[0]]
    row = int(s[1])
    if not in_bounds(row, col):
        raise ValueError("Square out of bounds: " + s)
    return (row, col)

def pos_to_algebraic(pos: Position) -> str:
    r, c = pos
    return f"{COL_TO_FILE[c]}{r}"

# --- PIECE CLASSES ---
class Piece:
    def __init__(self, row: int, col: int, symbol: str, color: str):
        self.row = row
        self.col = col
        self.color = color
        self.symbol = symbol if color == "white" else symbol.lower()
        self.moved = False
        self.name = symbol.lower()

    def pos(self) -> Position:
        return (self.row, self.col)

    def set_pos(self, r: int, c: int):
        self.row, self.col = r, c

    def is_enemy(self, board_array: List[List[str]], r: int, c: int) -> bool:
        ch = board_array[r-1][c-1]
        if ch == " ":
            return False
        return ch.islower() if self.color == "white" else ch.isupper()
        
    def is_same_color(self, board_array: List[List[str]], r: int, c: int) -> bool:
        ch = board_array[r-1][c-1]
        if ch == " ":
            return False
        return (ch.islower() and self.color == "black") or (ch.isupper() and self.color == "white")

    def gen_moves(self, game: "Game") -> List[Position]:
        raise NotImplementedError

class SlidingPiece(Piece):
    directions: List[Tuple[int, int]] = []

    def gen_moves(self, game: "Game") -> List[Position]:
        arr = game.board.return_array()
        moves: List[Position] = []
        for dr, dc in self.directions:
            r, c = self.row + dr, self.col + dc
            while in_bounds(r, c):
                cell = arr[r-1][c-1]
                if cell == " ":
                    moves.append((r, c))
                else:
                    if self.is_enemy(arr, r, c):
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves

class Rook(SlidingPiece):
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    def __init__(self, r, c, color):
        super().__init__(r, c, "R", color)

class Bishop(SlidingPiece):
    directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
    def __init__(self, r, c, color):
        super().__init__(r, c, "B", color)

class Queen(SlidingPiece):
    directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    def __init__(self, r, c, color):
        super().__init__(r, c, "Q", color)

class Knight(Piece):
    DELTAS = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
    def __init__(self, r, c, color):
        super().__init__(r, c, "N", color)
    def gen_moves(self, game: "Game") -> List[Position]:
        arr = game.board.return_array()
        moves: List[Position] = []
        for dr, dc in self.DELTAS:
            r, c = self.row + dr, self.col + dc
            if in_bounds(r, c):
                ch = arr[r-1][c-1]
                if ch == " " or self.is_enemy(arr, r, c):
                    moves.append((r, c))
        return moves

class King(Piece):
    DELTAS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def __init__(self, r, c, color):
        super().__init__(r, c, "K", color)
        self.can_castle_king_side = True
        self.can_castle_queen_side = True

    def gen_moves(self, game: "Game") -> List[Position]:
        arr = game.board.return_array()
        moves: List[Position] = []
        for dr, dc in self.DELTAS:
            r, c = self.row + dr, self.col + dc
            if in_bounds(r, c):
                ch = arr[r-1][c-1]
                if ch == " " or self.is_enemy(arr, r, c):
                    moves.append((r, c))
        if not self.moved: # Removed the `and not game.in_check(self.color)` to fix recursion
            row = 1 if self.color == "white" else 8
            if game.can_castle(self.color, king_side=True):
                moves.append((row, 7))
            if game.can_castle(self.color, king_side=False):
                moves.append((row, 3))
        return moves

class Pawn(Piece):
    def __init__(self, r, c, color):
        super().__init__(r, c, "P", color)

    def gen_moves(self, game: "Game") -> List[Position]:
        arr = game.board.return_array()
        moves: List[Position] = []
        dir = 1 if self.color == "white" else -1
        start_row = 2 if self.color == "white" else 7

        # Forward one square
        r1, c1 = self.row + dir, self.col
        if in_bounds(r1, c1) and arr[r1-1][c1-1] == " ":
            moves.append((r1, c1))

            # Forward two squares (only if pawn hasn't moved and path is clear)
            if not self.moved and self.row == start_row:
                r2 = self.row + 2*dir
                if in_bounds(r2, c1) and arr[r2-1][c1-1] == " ":
                    moves.append((r2, c1))

        # Diagonal captures (including en passant)
        for dc in (-1, 1):
            r, c = self.row + dir, self.col + dc
            if in_bounds(r, c):
                if self.is_enemy(arr, r, c):
                    moves.append((r, c))
                elif game.en_passant_target == (r, c):
                    moves.append((r, c))

        return moves

class Game:
    def __init__(self):
        self.board = Board()
        self.pieces: List[Piece] = []
        self.to_move = "white"
        self.move_number = 1
        self.captured_pieces = {"white": [], "black": []}
        self.kings: Dict[str, King] = {"white": King(1,5,"white"), "black": King(8,5,"black")}
        self.en_passant_target: Optional[Position] = None
        self.history: List[Tuple[Any, ...]] = []
        self.halfmove_clock = 0
        self.full_move_history: List[str] = []
        self.init_board()

    def init_board(self):
        self.board = Board()
        self.pieces = []
        self.to_move = "white"
        self.move_number = 1
        self.captured_pieces = {"white": [], "black": []}
        self.kings = {"white": King(1,5,"white"), "black": King(8,5,"black")}
        self.en_passant_target = None
        self.history = []
        self.halfmove_clock = 0
        self.full_move_history = []
        self.board.put_piece(1, 1, "R")
        self.board.put_piece(1, 2, "N")
        self.board.put_piece(1, 3, "B")
        self.board.put_piece(1, 4, "Q")
        self.board.put_piece(1, 5, "K")
        self.board.put_piece(1, 6, "B")
        self.board.put_piece(1, 7, "N")
        self.board.put_piece(1, 8, "R")
        self.board.put_piece(8, 1, "r")
        self.board.put_piece(8, 2, "n")
        self.board.put_piece(8, 3, "b")
        self.board.put_piece(8, 4, "q")
        self.board.put_piece(8, 5, "k")
        self.board.put_piece(8, 6, "b")
        self.board.put_piece(8, 7, "n")
        self.board.put_piece(8, 8, "r")
        for c in range(1, 9):
            self.board.put_piece(2, c, "P")
            self.board.put_piece(7, c, "p")
        
        self.pieces = self._create_pieces_from_board()
        self.history.append(self._snapshot())

    def reset_game(self):
        self.init_board()
    
    def piece_at(self, pos: Position) -> Optional[Piece]:
        for piece in self.pieces:
            if piece.pos() == pos:
                return piece
        return None
    
    def _create_pieces_from_board(self) -> List[Piece]:
        pieces = []
        for r in range(1, 9):
            for c in range(1, 9):
                symbol = self.board.get_piece(r, c)
                if symbol != " ":
                    color = "white" if symbol.isupper() else "black"
                    piece: Piece
                    if symbol.lower() == "p": piece = Pawn(r, c, color)
                    elif symbol.lower() == "r": piece = Rook(r, c, color)
                    elif symbol.lower() == "n": piece = Knight(r, c, color)
                    elif symbol.lower() == "b": piece = Bishop(r, c, color)
                    elif symbol.lower() == "q": piece = Queen(r, c, color)
                    elif symbol.lower() == "k": piece = King(r, c, color)
                    else: continue
                    pieces.append(piece)
                    
                    if symbol.lower() == "k":
                        self.kings[color] = piece
        return pieces

    def _get_pieces_for_color(self, color: str) -> List[Piece]:
        return [p for p in self.pieces if p.color == color]

    def is_attacked(self, pos, color):
        """
        Checks if a given position is attacked by the specified color.
        This version avoids recursion by not calling gen_moves.
        """
        row, col = pos

        # Check for pawn attacks
        pawn_direction = -1 if color == "white" else 1
        pawn_attack_rows = [row + pawn_direction]
        pawn_attack_cols = [col - 1, col + 1]

        for attack_row in pawn_attack_rows:
            for attack_col in pawn_attack_cols:
                if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                    piece = self.board.piece_at((attack_row, attack_col))
                    if piece and piece.color == color and piece.name == "pawn":
                        return True

        # Check for Knight attacks
        knight_moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]
        for move_row, move_col in knight_moves:
            if 0 <= move_row < 8 and 0 <= move_col < 8:
                piece = self.board.piece_at((move_row, move_col))
                if piece and piece.color == color and piece.name == "knight":
                    return True

        # Check for straight line attacks (Rooks and Queens)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.board.piece_at((r, c))
                if piece:
                    if piece.color == color and (piece.name == "rook" or piece.name == "queen"):
                        return True
                    else:
                        break
        
        # Check for diagonal attacks (Bishops and Queens)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                piece = self.board.piece_at((r, c))
                if piece:
                    if piece.color == color and (piece.name == "bishop" or piece.name == "queen"):
                        return True
                    else:
                        break

        # Check for King attacks
        king_moves = [
            (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
            (row, col - 1), (row, col + 1),
            (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)
        ]
        for move_row, move_col in king_moves:
            if 0 <= move_row < 8 and 0 <= move_col < 8:
                piece = self.board.piece_at((move_row, move_col))
                if piece and piece.color == color and piece.name == "king":
                    return True

        return False

    def in_check(self, color: str) -> bool:
        """
        Checks if the king of the given color is in check.
        """
        king = self.kings[color]
        if not king:
            return False
        return self.is_attacked(king.pos(), "white" if color == "black" else "black")

    def _can_move_piece_without_check(self, piece: Piece, dst: Position) -> bool:
        snapshot = self._snapshot()
        self._temp_move(piece, dst)
        is_safe = not self.in_check(piece.color)
        self._restore_snapshot(snapshot)
        return is_safe

    def legal_moves_for(self, piece: Piece) -> List[Position]:
        if piece.color != self.to_move:
            return []
        all_moves = piece.gen_moves(self)
        legal_moves = [move for move in all_moves if self._can_move_piece_without_check(piece, move)]
        return legal_moves
    
    def get_all_legal_moves(self, color: str) -> List[Tuple[Position, Position]]:
        moves = []
        for piece in self._get_pieces_for_color(color):
            for dest in self.legal_moves_for(piece):
                moves.append((piece.pos(), dest))
        return moves

    def make_move(self, src: Position, dst: Position, promo_piece: Optional[str] = None) -> bool:
        piece = self.piece_at(src)
        if not piece or piece.color != self.to_move or dst not in self.legal_moves_for(piece):
            return False

        captured_piece = self.piece_at(dst)
        
        # Snapshot for `outcome` check
        snapshot = self._snapshot()

        # Handle Castling
        is_castle = isinstance(piece, King) and abs(src[1] - dst[1]) == 2
        if is_castle:
            rook_src, rook_dst = None, None
            if dst[1] == 7: # King-side castle
                rook_src = (src[0], 8)
                rook_dst = (src[0], 6)
            elif dst[1] == 3: # Queen-side castle
                rook_src = (src[0], 1)
                rook_dst = (src[0], 4)
            
            if rook_src and rook_dst:
                rook = self.piece_at(rook_src)
                if rook:
                    self.board.put_piece(rook_src[0], rook_src[1], " ")
                    self.board.put_piece(rook_dst[0], rook_dst[1], rook.symbol)
                    rook.set_pos(rook_dst[0], rook_dst[1])
                    rook.moved = True

        # Handle En Passant
        is_en_passant = isinstance(piece, Pawn) and dst == self.en_passant_target
        if is_en_passant:
            captured_pos = (src[0], dst[1]) if piece.color == "white" else (dst[0] + 1, dst[1])
            captured_piece = self.piece_at(captured_pos)
            if captured_piece:
                self.pieces.remove(captured_piece)
                self.captured_pieces[self.to_move].append(captured_piece)
                self.board.put_piece(captured_pos[0], captured_pos[1], " ")

        # Update board and piece position
        self.board.put_piece(src[0], src[1], " ")
        if captured_piece and not is_en_passant:
            self.pieces.remove(captured_piece)
            self.captured_pieces[self.to_move].append(captured_piece)
        
        # Handle Pawn Promotion
        if isinstance(piece, Pawn) and (dst[0] == 8 or dst[0] == 1) and promo_piece:
            promoted_piece: Piece
            if promo_piece.lower() == 'q': promoted_piece = Queen(dst[0], dst[1], piece.color)
            elif promo_piece.lower() == 'r': promoted_piece = Rook(dst[0], dst[1], piece.color)
            elif promo_piece.lower() == 'b': promoted_piece = Bishop(dst[0], dst[1], piece.color)
            elif promo_piece.lower() == 'n': promoted_piece = Knight(dst[0], dst[1], piece.color)
            else: return False # Should not happen with the GUI
            
            self.pieces.remove(piece)
            self.pieces.append(promoted_piece)
            self.board.put_piece(dst[0], dst[1], promoted_piece.symbol)
            promoted_piece.moved = True
            
        else:
            self.board.put_piece(dst[0], dst[1], piece.symbol)
            piece.set_pos(dst[0], dst[1])
            piece.moved = True

        # Update En Passant target
        self.en_passant_target = None
        if isinstance(piece, Pawn) and abs(src[0] - dst[0]) == 2:
            self.en_passant_target = (src[0] + (1 if piece.color == "white" else -1), src[1])

        # Update halfmove clock
        if captured_piece or isinstance(piece, Pawn):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.to_move = "black" if self.to_move == "white" else "white"
        if self.to_move == "white":
            self.move_number += 1

        # Check for three-fold repetition
        self.full_move_history.append(self.board_to_fen())
        
        self.history.append(self._snapshot())

        return True
    
    def _temp_move(self, piece: Piece, dst: Position):
        # A lightweight move for check validation, no history or state changes
        src = piece.pos()
        captured_symbol = self.board.get_piece(dst[0], dst[1])
        
        self.board.put_piece(src[0], src[1], " ")
        self.board.put_piece(dst[0], dst[1], piece.symbol)
        
        # The piece object's position is not updated here, to be reverted
        # The captured piece is not removed from the pieces list
        
        # Castling: move rook without updating its object
        if isinstance(piece, King) and abs(src[1] - dst[1]) == 2:
            if dst[1] == 7: # King-side
                self.board.put_piece(src[0], 8, " ")
                self.board.put_piece(src[0], 6, Rook(src[0], 8, piece.color).symbol)
            elif dst[1] == 3: # Queen-side
                self.board.put_piece(src[0], 1, " ")
                self.board.put_piece(src[0], 4, Rook(src[0], 1, piece.color).symbol)

    def is_attacked(self, pos, color):
        """
        Checks if a given position is attacked by the specified color.
        This version avoids recursion by not calling gen_moves and uses correct
        1-based coordinates for the board.
        """
        row, col = pos

        # Check for pawn attacks
        pawn_direction = -1 if color == "white" else 1
        
        # Corrected loop for pawns
        for dc in [-1, 1]:
            attack_row, attack_col = row + pawn_direction, col + dc
            if 1 <= attack_row <= 8 and 1 <= attack_col <= 8:
                piece = self.piece_at((attack_row, attack_col))
                if piece and piece.color == color and piece.name == "pawn":
                    return True

        # Check for Knight attacks
        knight_moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]
        for move_row, move_col in knight_moves:
            if 1 <= move_row <= 8 and 1 <= move_col <= 8:
                piece = self.piece_at((move_row, move_col))
                if piece and piece.color == color and piece.name == "knight":
                    return True

        # Check for straight line attacks (Rooks and Queens)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (1 <= r <= 8 and 1 <= c <= 8):
                    break
                piece = self.piece_at((r, c))
                if piece:
                    if piece.color == color and (piece.name == "rook" or piece.name == "queen"):
                        return True
                    else:
                        break
        
        # Check for diagonal attacks (Bishops and Queens)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (1 <= r <= 8 and 1 <= c <= 8):
                    break
                piece = self.piece_at((r, c))
                if piece:
                    if piece.color == color and (piece.name == "bishop" or piece.name == "queen"):
                        return True
                    else:
                        break

        # Check for King attacks
        king_moves = [
            (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
            (row, col - 1), (row, col + 1),
            (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)
        ]
        for move_row, move_col in king_moves:
            if 1 <= move_row <= 8 and 1 <= move_col <= 8:
                piece = self.piece_at((move_row, move_col))
                if piece and piece.color == color and piece.name == "king":
                    return True

        return False

    def in_check(self, color: str) -> bool:
        """
        Checks if the king of the given color is in check.
        """
        king = self.kings[color]
        if not king:
            return False
        return self.is_attacked(king.pos(), "white" if color == "black" else "black")

    def can_castle(self, color: str, king_side: bool) -> bool:
        """
        Checks if castling is a legal move.
        """
        king_pos = self.kings[color].pos()
        king = self.piece_at(king_pos)
        
        # Check if king or rook has moved
        if king.moved:
            return False
        
        row = 1 if color == "white" else 8
        
        if king_side:
            rook_pos = (row, 8)
            rook = self.piece_at(rook_pos)
            if not rook or not isinstance(rook, Rook) or rook.moved:
                return False
            # Check if squares between king and rook are empty
            if self.board.get_piece(row, 6) != " " or self.board.get_piece(row, 7) != " ":
                return False
            # Check if king is in check or moves through an attacked square
            if self.in_check(color) or self.is_attacked((row, 6), "white" if color == "black" else "black") or self.is_attacked((row, 7), "white" if color == "black" else "black"):
                return False
        else:  # Queen-side
            rook_pos = (row, 1)
            rook = self.piece_at(rook_pos)
            if not rook or not isinstance(rook, Rook) or rook.moved:
                return False
            # Check if squares between king and rook are empty
            if self.board.get_piece(row, 2) != " " or self.board.get_piece(row, 3) != " " or self.board.get_piece(row, 4) != " ":
                return False
            # Check if king is in check or moves through an attacked square
            if self.in_check(color) or self.is_attacked((row, 3), "white" if color == "black" else "black") or self.is_attacked((row, 4), "white" if color == "black" else "black"):
                return False
        
        return True
    def _check_for_three_fold_repetition(self) -> bool:
        current_fen = self.board_to_fen()
        count = self.full_move_history.count(current_fen)
        return count >= 3

    def _check_for_fifty_move_rule(self) -> bool:
        return self.halfmove_clock >= 50

    def outcome(self) -> Optional[str]:
        if not self.get_all_legal_moves(self.to_move):
            if self.in_check(self.to_move):
                winner = "black" if self.to_move == "white" else "white"
                return f"{winner} wins"
            else:
                return "stalemate"
        if self._check_for_three_fold_repetition():
            return "threefold repetition"
        if self._check_for_fifty_move_rule():
            return "fifty move rule"
        
        return None
        
    def _snapshot(self) -> Any:
        # Save a copy of the current game state
        state = {
            "board_array": [row[:] for row in self.board.array],
            "pieces": [p for p in self.pieces], # shallow copy
            "to_move": self.to_move,
            "move_number": self.move_number,
            "captured_pieces": {c: [p for p in pieces] for c, pieces in self.captured_pieces.items()},
            "kings": self.kings,
            "en_passant_target": self.en_passant_target,
            "halfmove_clock": self.halfmove_clock,
            "full_move_history": [s for s in self.full_move_history]
        }
        return state

    def _restore_snapshot(self, state: Any):
        # Restore a saved game state
        self.board.array = [row[:] for row in state["board_array"]]
        self.pieces = state["pieces"]
        self.to_move = state["to_move"]
        self.move_number = state["move_number"]
        self.captured_pieces = state["captured_pieces"]
        self.kings = state["kings"]
        self.en_passant_target = state["en_passant_target"]
        self.halfmove_clock = state["halfmove_clock"]
        self.full_move_history = state["full_move_history"]

    def piece_value(self, piece_symbol: str) -> int:
        symbol = piece_symbol.upper()
        return PIECE_VALUES.get(symbol, 0)
    
    def board_to_fen(self) -> str:
        fen = ""
        for r in range(7, -1, -1):
            empty_count = 0
            for c in range(8):
                piece = self.board.array[r][c]
                if piece == " ":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    fen += piece
            if empty_count > 0:
                fen += str(empty_count)
            if r > 0:
                fen += "/"
        
        fen += f" {self.to_move[0]}"
        
        castling = ""
        if self.kings["white"].can_castle_king_side: castling += "K"
        if self.kings["white"].can_castle_queen_side: castling += "Q"
        if self.kings["black"].can_castle_king_side: castling += "k"
        if self.kings["black"].can_castle_queen_side: castling += "q"
        if not castling:
            castling = "-"
        fen += f" {castling}"
        en_passant_target = "-"
        if self.en_passant_target:
            en_passant_target = pos_to_algebraic(self.en_passant_target)
        fen += f" {en_passant_target}"
        fen += f" {self.halfmove_clock} {self.move_number}"
        return fen

    def _create_custom_game(self, start_pos, turn, en_passant_target=None):
        self.init_board() # Reset to a clean state first
        self.board = Board()
        self.pieces = []
        rows = start_pos.split('/')
        for r_idx, row_str in enumerate(rows):
            c_idx = 0
            for char in row_str:
                if char.isdigit():
                    c_idx += int(char)
                else:
                    self.board.put_piece(8 - r_idx, c_idx + 1, char)
                    c_idx += 1
        self.pieces = self._create_pieces_from_board()
        self.to_move = turn
        self.en_passant_target = en_passant_target
        self.history.append(self._snapshot())

class ChessGUI:
    def __init__(self, game):
        self.game = game
        self.selected: Optional[Position] = None
        self.valid_moves: List[Position] = []
        self.promoting = False
        self.promotion_move: Optional[Position] = None
        self.game_over_text: Optional[str] = None
        self.game_mode: Optional[str] = "Start"
        self.sound_on = True
        self.piece_images: Dict[str, pygame.Surface] = {}
        self.load_images()
        freq = 44100
        size = -16
        channels = 1
        buffer_size = 500
        period = freq // 1000
        volume = 12000
        sound_buffer = array.array('h', [0] * buffer_size)
        for i in range(buffer_size):
            if i % period < period / 2:
                sound_buffer[i] = volume
            else:
                sound_buffer[i] = -volume
        self.move_sound = pygame.mixer.Sound(sound_buffer)
        self.ai = AI(game, depth=2)
    def _piece_name(self, symbol: str) -> str:
        """Returns the full name of a piece based on its symbol."""
        symbol = symbol.lower()
        if symbol == 'p': return 'Pawn'
        if symbol == 'n': return 'Knight'
        if symbol == 'b': return 'Bishop'
        if symbol == 'r': return 'Rook'
        if symbol == 'q': return 'Queen'
        if symbol == 'k': return 'King'
        return ' '
    def load_images(self):
        """Loads all piece images with the color-type.png naming convention."""
        piece_map = {
            'p': 'pawn',
            'n': 'knight',
            'b': 'bishop',
            'r': 'rook',
            'q': 'queen',
            'k': 'king'
        }
        image_dir = 'pieces'
        if not os.path.exists(image_dir):
            print(f"Error: The '{image_dir}' directory was not found. Please create this folder and place your piece images inside.")
            return
        for color_name in ['white', 'black']:
            for symbol, piece_name in piece_map.items():
                filename = f"{color_name}-{piece_name}.png"
                img_path = os.path.join(image_dir, filename)
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    self.piece_images[color_name[0] + symbol] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                except pygame.error:
                    print(f"Error loading image {filename}. The file might be missing or corrupted.")
                    self.piece_images[color_name[0] + symbol] = None
        if len(self.piece_images) != 12 or any(img is None for img in self.piece_images.values()):
            print("Warning: Not all piece images were loaded successfully. Pieces may not display correctly.")

    def draw_board(self, lesson_info=None):
        """Draws the main board, pieces, and coordinates on all four sides."""
        # Calculate board offset to center it for the new screen width
        board_offset_x = (SCREEN_WIDTH - BOARD_SIZE_PX) // 2
        board_offset_y = (SCREEN_HEIGHT - BOARD_SIZE_PX) // 2
        # Draw chess board squares
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = WHITE if (row + col) % 2 == 0 else BLACK
                pygame.draw.rect(screen, color, (board_offset_x + col * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row - 1) * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        # Draw coordinates on all four sides
        coord_margin = 5
        for i in range(BOARD_SIZE):
            # Letters at top and bottom (a-h)
            letter = chr(ord('a') + i)
            text = FONT.render(letter, True, COORD_COLOR)
            screen.blit(text, (board_offset_x + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_width() // 2, board_offset_y - text.get_height() - coord_margin))
            screen.blit(text, (board_offset_x + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_width() // 2, board_offset_y + BOARD_SIZE_PX + coord_margin))
            # Numbers on left and right (1 at bottom, 8 at top)
            number = str(8 - i)
            text = FONT.render(number, True, COORD_COLOR)
            screen.blit(text, (board_offset_x - text.get_width() - coord_margin, board_offset_y + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_height() // 2))
            screen.blit(text, (board_offset_x + BOARD_SIZE_PX + coord_margin, board_offset_y + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text.get_height() // 2))
        # Highlight selected square
        if self.selected:
            row_idx, col_idx = self.selected[0] - 1, self.selected[1] - 1
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(HIGHLIGHT)
            screen.blit(s, (board_offset_x + col_idx * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row_idx - 1) * SQUARE_SIZE))
        # Highlight valid moves
        for move in self.valid_moves:
            row_idx, col_idx = move[0] - 1, move[1] - 1
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(MOVE_HIGHLIGHT)
            screen.blit(s, (board_offset_x + col_idx * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row_idx - 1) * SQUARE_SIZE))
        # Highlight king in check
        king_pos = self.game.kings.get(self.game.to_move)
        if king_pos and self.game.in_check(self.game.to_move):
            row_idx, col_idx = king_pos.pos()[0] - 1, king_pos.pos()[1] - 1
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(CHECK_RED)
            screen.blit(s, (board_offset_x + col_idx * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row_idx - 1) * SQUARE_SIZE))
        # Draw pieces with images
        for piece in self.game.pieces:
            piece_symbol = piece.symbol
            if piece_symbol != " ":
                piece_color_char = 'w' if piece_symbol.isupper() else 'b'
                image_key = piece_color_char + piece_symbol.lower()
                r, c = piece.pos()
                if image_key in self.piece_images and self.piece_images[image_key] is not None:
                    image = self.piece_images[image_key]
                    screen_y = board_offset_y + (BOARD_SIZE - r) * SQUARE_SIZE
                    screen_x = board_offset_x + (c - 1) * SQUARE_SIZE
                    screen.blit(image, (screen_x, screen_y))
    def draw_sidebar(self, turn_label: str):
        # Sidebar for move history, captured pieces, and controls
        sidebar_x = SCREEN_WIDTH - 250
        sidebar_y = 50
        pygame.draw.rect(screen, BUTTON_COLOR, (sidebar_x - 10, sidebar_y - 10, 240, SCREEN_HEIGHT - 60))
        
        # Display current turn
        turn_text = BOLD_FONT.render(turn_label, True, TEXT_COLOR)
        screen.blit(turn_text, (sidebar_x, sidebar_y))

        # Display captured pieces
        captured_x = sidebar_x
        captured_y = sidebar_y + 50
        
        white_captured_text = FONT.render("White's captured pieces:", True, TEXT_COLOR)
        screen.blit(white_captured_text, (captured_x, captured_y))
        
        self._draw_captured_pieces(captured_x, captured_y + 30, self.game.captured_pieces['white'])

        black_captured_text = FONT.render("Black's captured pieces:", True, TEXT_COLOR)
        screen.blit(black_captured_text, (captured_x, captured_y + 100))
        
        self._draw_captured_pieces(captured_x, captured_y + 130, self.game.captured_pieces['black'])

        # Display move history
        history_x = sidebar_x
        history_y = captured_y + 200
        history_text_title = FONT.render("Move History:", True, TEXT_COLOR)
        screen.blit(history_text_title, (history_x, history_y))

        history_list_y = history_y + 30
        for i, move in enumerate(self.game.full_move_history):
            if i >= 10: break
            move_text = FONT.render(move, True, TEXT_COLOR)
            screen.blit(move_text, (history_x, history_list_y + i * 25))

        # Buttons
        button_width, button_height = 100, 40
        button_y = SCREEN_HEIGHT - 100
        
        # New Game Button
        new_game_rect = pygame.Rect(sidebar_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, BUTTON_COLOR, new_game_rect)
        new_game_text = FONT.render("New Game", True, TEXT_COLOR)
        screen.blit(new_game_text, (new_game_rect.centerx - new_game_text.get_width() // 2, new_game_rect.centery - new_game_text.get_height() // 2))

    def _draw_captured_pieces(self, x, y, pieces: List[Piece]):
        piece_symbols = [p.symbol for p in pieces]
        text = FONT.render(" ".join(piece_symbols), True, TEXT_COLOR)
        screen.blit(text, (x, y))

    def draw_game_over(self):
        if self.game_over_text:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            text_surface = LARGE_FONT.render(self.game_over_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            
            # Restart button
            restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
            pygame.draw.rect(screen, BUTTON_COLOR, restart_rect)
            restart_text = BOLD_FONT.render("Restart", True, TEXT_COLOR)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            screen.blit(restart_text, restart_text_rect)

            return restart_rect
        return None

    def draw_promotion_dialog(self, king_pos_x, king_pos_y):
        promotion_pieces = ['Q', 'R', 'B', 'N']
        dialog_width = SQUARE_SIZE * len(promotion_pieces)
        dialog_height = SQUARE_SIZE
        dialog_rect = pygame.Rect(king_pos_x, king_pos_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2)
        
        piece_color_char = 'w' if self.game.to_move == "white" else 'b'
        
        for i, piece_symbol in enumerate(promotion_pieces):
            image_key = piece_color_char + piece_symbol.lower()
            if image_key in self.piece_images and self.piece_images[image_key] is not None:
                image = self.piece_images[image_key]
                screen.blit(image, (king_pos_x + i * SQUARE_SIZE, king_pos_y))
        
        return dialog_rect, promotion_pieces

    def draw_start_menu(self):
        menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        menu_bg.fill((0, 0, 0, 150))
        screen.blit(menu_bg, (0, 0))

        title_text = LARGE_FONT.render("Chess Engine", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        screen.blit(title_text, title_rect)
        
        # Buttons
        button_width, button_height = 200, 60
        
        # Play vs AI Button
        play_ai_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2, button_width, button_height)
        pygame.draw.rect(screen, BUTTON_COLOR, play_ai_rect)
        play_ai_text = BOLD_FONT.render("Play vs AI", True, TEXT_COLOR)
        play_ai_text_rect = play_ai_text.get_rect(center=play_ai_rect.center)
        screen.blit(play_ai_text, play_ai_text_rect)

        # Play vs Player Button
        play_player_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 80, button_width, button_height)
        pygame.draw.rect(screen, BUTTON_COLOR, play_player_rect)
        play_player_text = BOLD_FONT.render("Play vs Player", True, TEXT_COLOR)
        play_player_text_rect = play_player_text.get_rect(center=play_player_rect.center)
        screen.blit(play_player_text, play_player_text_rect)
        
        # Lessons Button
        lessons_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + 160, button_width, button_height)
        pygame.draw.rect(screen, BUTTON_COLOR, lessons_rect)
        lessons_text = BOLD_FONT.render("Lessons", True, TEXT_COLOR)
        lessons_text_rect = lessons_text.get_rect(center=lessons_rect.center)
        screen.blit(lessons_text, lessons_text_rect)

        return play_ai_rect, play_player_rect, lessons_rect
    
    def run(self):
        running = True
        ai_turn = False
        while running:
            
            # AI's Turn
            if self.game.to_move == "black" and self.game_mode == "AI" and not self.promoting and not self.game_over_text:
                if not ai_turn:
                    print("AI is thinking...")
                    ai_turn = True
                else:
                    move = self.ai.get_ai_move(self.game)
                    if move:
                        src, dst, promo = move
                        self.game.make_move(src, dst, promo)
                        if self.sound_on: self.move_sound.play()
                        if self.game.outcome():
                            self.game_over_text = self.game.outcome()
                        self.selected = None
                        self.valid_moves = []
                    else:
                        # AI has no legal moves, game over
                        self.game_over_text = self.game.outcome()
                    ai_turn = False

            screen.fill(BACKGROUND_COLOR)
            
            if self.game_mode == "Start":
                play_ai_rect, play_player_rect, lessons_rect = self.draw_start_menu()
            elif self.game_mode == "Lessons":
                # Draw lesson menu
                pass
            else: # Game mode is "AI" or "Player"
                turn_label = f"{self.game.to_move.capitalize()}'s Turn"
                self.draw_board()
                self.draw_sidebar(turn_label)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_mode == "Start":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if play_ai_rect.collidepoint(event.pos):
                            self.game_mode = "AI"
                            self.game.reset_game()
                        elif play_player_rect.collidepoint(event.pos):
                            self.game_mode = "Player"
                            self.game.reset_game()
                        elif lessons_rect.collidepoint(event.pos):
                            self.game_mode = "Lessons"
                            # Load lessons or show menu

                elif self.game_mode == "Lessons":
                    # Handle lesson menu events
                    pass
                else: # Game mode is "AI" or "Player"
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over_text and not self.promoting:
                        mouse_x, mouse_y = event.pos
                        board_offset_x = (SCREEN_WIDTH - BOARD_SIZE_PX) // 2
                        board_offset_y = (SCREEN_HEIGHT - BOARD_SIZE_PX) // 2
                        if board_offset_x <= mouse_x < board_offset_x + BOARD_SIZE_PX and \
                           board_offset_y <= mouse_y < board_offset_y + BOARD_SIZE_PX:
                            
                            col = (mouse_x - board_offset_x) // SQUARE_SIZE + 1
                            row = BOARD_SIZE - ((mouse_y - board_offset_y) // SQUARE_SIZE)
                            pos = (row, col)

                            piece = self.game.piece_at(pos)
                            
                            if self.selected:
                                if pos in self.valid_moves:
                                    # Promotion check
                                    is_pawn = isinstance(self.game.piece_at(self.selected), Pawn)
                                    is_promo_row = (row == 8 and self.game.to_move == "white") or (row == 1 and self.game.to_move == "black")
                                    if is_pawn and is_promo_row:
                                        self.promoting = True
                                        self.promotion_move = (self.selected, pos)
                                    else:
                                        self.game.make_move(self.selected, pos)
                                        if self.sound_on: self.move_sound.play()
                                        if self.game.outcome():
                                            self.game_over_text = self.game.outcome()
                                        self.selected = None
                                        self.valid_moves = []
                                        ai_turn = False
                                else:
                                    self.selected = None
                                    self.valid_moves = []
                            
                            if piece and piece.color == self.game.to_move:
                                self.selected = pos
                                self.valid_moves = self.game.legal_moves_for(piece)
                        
                        else: # Clicked outside the board
                            self.selected = None
                            self.valid_moves = []

                    elif self.game_over_text and self.draw_game_over().collidepoint(event.pos):
                        self.game_over_text = None
                        self.game.reset_game()
                        self.game_mode = "Start"

                    elif self.promoting:
                        # Handle promotion dialog click
                        promo_rect, promo_pieces = self.draw_promotion_dialog(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25)
                        if promo_rect.collidepoint(event.pos):
                            x, y = event.pos
                            index = (x - promo_rect.left) // SQUARE_SIZE
                            if 0 <= index < len(promo_pieces):
                                promo_choice = promo_pieces[index]
                                src, dst = self.promotion_move
                                self.game.make_move(src, dst, promo_choice)
                                if self.sound_on: self.move_sound.play()
                                if self.game.outcome():
                                    self.game_over_text = self.game.outcome()
                                self.promoting = False
                                self.promotion_move = None
                                self.selected = None
                                self.valid_moves = []
                                ai_turn = False
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

class AI:
    def __init__(self, game: Game, depth: int):
        self.game = game
        self.depth = depth

    def get_ai_move(self, game: Game) -> Optional[Tuple[Position, Position, Optional[str]]]:
        self.game = game
        best_move, _ = self.minimax(self.depth, "black")
        return best_move

    def minimax(self, depth: int, player: str) -> Tuple[Optional[Tuple[Position, Position, Optional[str]]], int]:
        if depth == 0 or self.game.outcome():
            return None, self.evaluate_board()

        best_move = None
        if player == "black":
            max_eval = float('-inf')
            legal_moves = self.game.get_all_legal_moves(player)
            for move in legal_moves:
                src, dst = move
                piece = self.game.piece_at(src)
                promo_piece = None
                
                # Check for pawn promotion
                if isinstance(piece, Pawn) and (dst[0] == 8 or dst[0] == 1):
                    # AI always promotes to queen for simplicity
                    promo_piece = 'q'

                snapshot = self.game._snapshot()
                self.game.make_move(src, dst, promo_piece)
                _, eval = self.minimax(depth - 1, "white")
                self.game._restore_snapshot(snapshot)

                if eval > max_eval:
                    max_eval = eval
                    best_move = (src, dst, promo_piece)
            return best_move, max_eval
        else: # white
            min_eval = float('inf')
            legal_moves = self.game.get_all_legal_moves(player)
            for move in legal_moves:
                src, dst = move
                piece = self.game.piece_at(src)
                promo_piece = None
                
                if isinstance(piece, Pawn) and (dst[0] == 8 or dst[0] == 1):
                    promo_piece = 'q'

                snapshot = self.game._snapshot()
                self.game.make_move(src, dst, promo_piece)
                _, eval = self.minimax(depth - 1, "black")
                self.game._restore_snapshot(snapshot)

                if eval < min_eval:
                    min_eval = eval
                    best_move = (src, dst, promo_piece)
            return best_move, min_eval

    def evaluate_board(self) -> int:
        score = 0
        for piece in self.game.pieces:
            value = PIECE_VALUES.get(piece.symbol.upper(), 0)
            if piece.color == "white":
                score += value
            else:
                score -= value
        
        # Check for game end states
        outcome = self.game.outcome()
        if outcome == "white wins":
            score += 10000
        elif outcome == "black wins":
            score -= 10000
        elif outcome == "stalemate":
            score = 0
            
        return score

if __name__ == "__main__":
    game = Game()
    gui = ChessGUI(game)
    gui.run()