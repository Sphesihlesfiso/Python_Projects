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
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700
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
LESSONS = [
    {
        "title": "Lesson 1: The Board and Pieces",
        "content": (
            "The chessboard is an 8x8 grid of squares.\n"
            "There are 32 pieces in total: 16 for each player.\n"
            "Each player has 8 pawns, 2 rooks, 2 knights, 2 bishops, 1 queen, and 1 king.\n"
            "White always moves first."
        )
    },
    {
        "title": "Lesson 2: The Pawn",
        "content": (
            "Pawns move forward one square, but on their first move they can move two squares.\n"
            "Pawns capture diagonally one square in front of them.\n"
            "They are the only piece that cannot move backward.\n"
            "When a pawn reaches the opposite side of the board, it can be promoted to a queen, rook, bishop, or knight."
        )
    },
    {
        "title": "Lesson 3: The Rook",
        "content": (
            "Rooks move in straight lines, horizontally or vertically.\n"
            "They can move any number of empty squares in a single turn.\n"
            "Rooks are very powerful in the endgame when the board is more open.\n"
            "A special move called 'castling' can be performed with the king and a rook."
        )
    },
]
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
        if not self.moved: 
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
        
        # Check for king capture
        if captured_piece and captured_piece.name == "king":
            return False

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
                return f"{winner} wins by checkmate"
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
        # The following needs to be fixed to reflect the King's move history, not a global flag
        white_king_moved = self.kings["white"].moved
        black_king_moved = self.kings["black"].moved
        white_kingside_rook_moved = self.piece_at((1, 8)) is None or self.piece_at((1, 8)).moved
        white_queenside_rook_moved = self.piece_at((1, 1)) is None or self.piece_at((1, 1)).moved
        black_kingside_rook_moved = self.piece_at((8, 8)) is None or self.piece_at((8, 8)).moved
        black_queenside_rook_moved = self.piece_at((8, 1)) is None or self.piece_at((8, 1)).moved

        if not white_king_moved and not white_kingside_rook_moved:
            castling += "K"
        if not white_king_moved and not white_queenside_rook_moved:
            castling += "Q"
        if not black_king_moved and not black_kingside_rook_moved:
            castling += "k"
        if not black_king_moved and not black_queenside_rook_moved:
            castling += "q"

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
        
        pygame.mixer.init()
        try:
            self.sound_move = pygame.mixer.Sound(os.path.join("sounds", "move.wav"))
            self.sound_capture = pygame.mixer.Sound(os.path.join("sounds", "capture.wav"))
            self.sound_check = pygame.mixer.Sound(os.path.join("sounds", "check.wav"))
            self.sound_game_over = pygame.mixer.Sound(os.path.join("sounds", "game_over.wav"))
            self.sound_checkmate = pygame.mixer.Sound(os.path.join("sounds", "checkmate.wav"))
        except pygame.error:
            print("Sound files not found. Sounds will be disabled.")
            self.sound_on = False

        self.load_images()
        self.screen_changed_callback = None
        self.current_lesson: Optional[Dict[str, str]] = None
    
    def set_screen_changed_callback(self, callback):
        if callable(callback):
            self.screen_changed_callback = callback
    
    def on_screen_changed(self):
        if self.screen_changed_callback:
            self.screen_changed_callback()
    
    def load_images(self):
        piece_map = {
            'P': 'white-pawn.png', 'R': 'white-rook.png', 'N': 'white-knight.png',
            'B': 'white-bishop.png', 'Q': 'white-queen.png', 'K': 'white-king.png',
            'p': 'black-pawn.png', 'r': 'black-rook.png', 'n': 'black-knight.png',
            'b': 'black-bishop.png', 'q': 'black-queen.png', 'k': 'black-king.png'
        }
        
        image_loaded = False
        image_folder = "pieces" 
        for symbol, filename in piece_map.items():
            img_path = os.path.join(image_folder, filename)
            if os.path.exists(img_path):
                try:
                    self.piece_images[symbol] = pygame.transform.scale(
                        pygame.image.load(img_path), (SQUARE_SIZE, SQUARE_SIZE)
                    )
                    image_loaded = True
                except pygame.error as e:
                    print(f"Error loading image {img_path}: {e}")
                    image_loaded = False
                    break 

        if not image_loaded:
            print("Could not find piece images or an error occurred. Using fallback shapes.")
            white_color = (255, 255, 255)
            black_color = (0, 0, 0)
            
            for piece_symbol, color in [
                ('P', white_color), ('R', white_color), ('N', white_color),
                ('B', white_color), ('Q', white_color), ('K', white_color),
                ('p', black_color), ('r', black_color), ('n', black_color),
                ('b', black_color), ('q', black_color), ('k', black_color),
            ]:
                surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                
                if piece_symbol.lower() == 'p':
                    pygame.draw.circle(surface, color, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 4)
                elif piece_symbol.lower() == 'r':
                    pygame.draw.rect(surface, color, (SQUARE_SIZE // 4, SQUARE_SIZE // 4, SQUARE_SIZE // 2, SQUARE_SIZE // 2))
                elif piece_symbol.lower() == 'n':
                    pygame.draw.polygon(surface, color, [
                        (SQUARE_SIZE//2, SQUARE_SIZE//4), (SQUARE_SIZE//4, SQUARE_SIZE//2),
                        (SQUARE_SIZE//2, SQUARE_SIZE//2), (SQUARE_SIZE*3//4, SQUARE_SIZE//2)
                    ])
                elif piece_symbol.lower() == 'b':
                    pygame.draw.circle(surface, color, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 3)
                    pygame.draw.polygon(surface, color, [
                        (SQUARE_SIZE // 2, SQUARE_SIZE // 3), (SQUARE_SIZE // 4, SQUARE_SIZE * 2 // 3),
                        (SQUARE_SIZE * 3 // 4, SQUARE_SIZE * 2 // 3)
                    ])
                elif piece_symbol.lower() == 'q':
                    pygame.draw.circle(surface, color, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 2)
                elif piece_symbol.lower() == 'k':
                    pygame.draw.circle(surface, color, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 2)
                    pygame.draw.line(surface, (255-color[0], 255-color[1], 255-color[2]), (SQUARE_SIZE//2 - 10, SQUARE_SIZE//2), (SQUARE_SIZE//2 + 10, SQUARE_SIZE//2), 3)
                    pygame.draw.line(surface, (255-color[0], 255-color[1], 255-color[2]), (SQUARE_SIZE//2, SQUARE_SIZE//2 - 10), (SQUARE_SIZE//2, SQUARE_SIZE//2 + 10), 3)
                
                self.piece_images[piece_symbol] = surface

    def draw_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = WHITE if (r + c) % 2 == 0 else BLACK
                rect = pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, color, rect)

        if self.selected:
            pygame.draw.rect(screen, HIGHLIGHT, (
                (self.selected[1] - 1) * SQUARE_SIZE,
                (BOARD_SIZE - self.selected[0]) * SQUARE_SIZE,
                SQUARE_SIZE,
                SQUARE_SIZE
            ), 5)
            
        if self.game.in_check(self.game.to_move):
            king_pos = self.game.kings[self.game.to_move].pos()
            if king_pos:
                pygame.draw.rect(screen, CHECK_RED, (
                    (king_pos[1] - 1) * SQUARE_SIZE,
                    (BOARD_SIZE - king_pos[0]) * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                ), 5)

        for move in self.valid_moves:
            pygame.draw.circle(screen, MOVE_HIGHLIGHT, (
                (move[1] - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
                (BOARD_SIZE - move[0]) * SQUARE_SIZE + SQUARE_SIZE // 2
            ), SQUARE_SIZE // 8)
            
    def draw_pieces(self):
        for piece in self.game.pieces:
            img = self.piece_images.get(piece.symbol)
            if img:
                screen.blit(img, (
                    (piece.col - 1) * SQUARE_SIZE,
                    (BOARD_SIZE - piece.row) * SQUARE_SIZE
                ))
    
    def draw_coords(self):
        for i in range(1, 9):
            text = FONT.render(COL_TO_FILE[i], True, COORD_COLOR)
            text_rect = text.get_rect(center=(
                (i - 1) * SQUARE_SIZE + SQUARE_SIZE // 2,
                BOARD_SIZE_PX + 20
            ))
            screen.blit(text, text_rect)
            
            text = FONT.render(str(i), True, COORD_COLOR)
            text_rect = text.get_rect(center=(
                -20,
                (BOARD_SIZE - i) * SQUARE_SIZE + SQUARE_SIZE // 2
            ))
            screen.blit(text, text_rect)
            
    def draw_start_menu(self):
        screen.fill(BACKGROUND_COLOR)
        title_text = LARGE_FONT.render("Chess Engine", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_text, title_rect)

        button_width, button_height = 200, 60
        button_y_start = SCREEN_HEIGHT // 2
        button_gap = 20
        
        self.play_button = self.create_button(
            "Play",
            (SCREEN_WIDTH // 2 - button_width // 2, button_y_start),
            (button_width, button_height)
        )
        self.lessons_button = self.create_button(
            "Lessons",
            (SCREEN_WIDTH // 2 - button_width // 2, button_y_start + button_height + button_gap),
            (button_width, button_height)
        )
        self.quit_button = self.create_button(
            "Quit",
            (SCREEN_WIDTH // 2 - button_width // 2, button_y_start + 2*(button_height + button_gap)),
            (button_width, button_height)
        )
        
        self.audio_button = self.create_button(
            "Sound: ON" if self.sound_on else "Sound: OFF",
            (SCREEN_WIDTH - 220, 20),
            (200, 50)
        )
        
        pygame.display.flip()

    def draw_lessons_menu(self):
        screen.fill(BACKGROUND_COLOR)
        title_text = LARGE_FONT.render("Lessons", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        button_width, button_height = 400, 60
        button_y_start = 200
        button_gap = 20
        self.lesson_buttons = []
        for i, lesson in enumerate(LESSONS):
            button = self.create_button(
                lesson['title'],
                (SCREEN_WIDTH // 2 - button_width // 2, button_y_start + i * (button_height + button_gap)),
                (button_width, button_height)
            )
            self.lesson_buttons.append(button)

        self.back_button = self.create_button(
            "Back",
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100),
            (200, 60)
        )

        pygame.display.flip()

    def draw_lesson_screen(self):
        screen.fill(BACKGROUND_COLOR)
        if self.current_lesson:
            title_text = BOLD_FONT.render(self.current_lesson['title'], True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(title_text, title_rect)
            
            content_text = self.current_lesson['content']
            y_offset = 150
            for line in content_text.split('\n'):
                text_surf = FONT.render(line, True, WHITE)
                screen.blit(text_surf, (100, y_offset))
                y_offset += 30
        
        self.back_button = self.create_button(
            "Back",
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100),
            (200, 60)
        )
        
        pygame.display.flip()

    def create_button(self, text, pos, size, hover_color=BUTTON_HOVER_COLOR):
        rect = pygame.Rect(pos, size)
        mouse_pos = pygame.mouse.get_pos()
        color = hover_color if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)
        
        text_surf = FONT.render(text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
        return rect

    def handle_start_menu_click(self, event):
        if event.button == 1:
            if self.play_button.collidepoint(event.pos):
                self.game_mode = "Game"
                self.game.reset_game()
                self.on_screen_changed()
            elif self.lessons_button.collidepoint(event.pos):
                self.game_mode = "Lessons"
                self.on_screen_changed()
            elif self.quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            elif self.audio_button.collidepoint(event.pos):
                self.sound_on = not self.sound_on
                
    def handle_lessons_menu_click(self, event):
        if event.button == 1:
            if self.back_button.collidepoint(event.pos):
                self.game_mode = "Start"
                self.on_screen_changed()
                return

            for i, button in enumerate(self.lesson_buttons):
                if button.collidepoint(event.pos):
                    self.current_lesson = LESSONS[i]
                    self.game_mode = "LessonContent"
                    self.on_screen_changed()
                    return

    def handle_lesson_content_click(self, event):
        if event.button == 1:
            if self.back_button.collidepoint(event.pos):
                self.current_lesson = None
                self.game_mode = "Lessons"
                self.on_screen_changed()

    def handle_mouse_click(self, event):
        if self.game_mode == "Start":
            self.handle_start_menu_click(event)
            return
        elif self.game_mode == "Lessons":
            self.handle_lessons_menu_click(event)
            return
        elif self.game_mode == "LessonContent":
            self.handle_lesson_content_click(event)
            return

        if self.game_over_text:
            self.handle_game_over_click(event)
            return

        x, y = event.pos
        col = x // SQUARE_SIZE + 1
        row = BOARD_SIZE - (y // SQUARE_SIZE)
        pos = (row, col)

        if not (1 <= row <= 8 and 1 <= col <= 8):
            return

        piece = self.game.piece_at(pos)

        if self.promoting:
            self.handle_promotion_click(pos)
            return
            
        if self.selected:
            if pos in self.valid_moves:
                if self.game.make_move(self.selected, pos):
                    if self.sound_on:
                        if self.game.piece_at(pos) and self.game.piece_at(pos).symbol.lower() != 'k':
                            self.sound_capture.play()
                        else:
                            self.sound_move.play()

                    self.selected = None
                    self.valid_moves = []
                    
                    if self.game.in_check(self.game.to_move) and self.sound_on:
                        self.sound_check.play()

                    self.game_over_text = self.game.outcome()
                    if self.game_over_text:
                        if self.sound_on:
                            self.sound_game_over.play()

                    moved_piece = self.game.piece_at(pos)
                    if isinstance(moved_piece, Pawn) and (moved_piece.row == 1 or moved_piece.row == 8):
                        self.promoting = True
                        self.promotion_move = pos
                else:
                    self.selected = None
                    self.valid_moves = []
            else:
                self.selected = pos if piece and piece.color == self.game.to_move else None
                selected_piece = self.game.piece_at(self.selected)
                self.valid_moves = self.game.legal_moves_for(selected_piece) if selected_piece else []
        else:
            if piece and piece.color == self.game.to_move:
                self.selected = pos
                self.valid_moves = self.game.legal_moves_for(piece)

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        text_surf = LARGE_FONT.render(self.game_over_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text_surf, text_rect)

        self.play_again_button = self.create_button(
            "Play Again",
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50),
            (200, 60)
        )
        self.back_to_menu_button = self.create_button(
            "Back to Menu",
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 130),
            (200, 60)
        )
    
    def handle_game_over_click(self, event):
        if event.button == 1:
            if self.play_again_button.collidepoint(event.pos):
                self.game.reset_game()
                self.game_over_text = None
            elif self.back_to_menu_button.collidepoint(event.pos):
                self.game_mode = "Start"
                self.game_over_text = None
                
    def draw_promotion_dialog(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        dialog_width, dialog_height = 400, 200
        dialog_rect = pygame.Rect(
            (SCREEN_WIDTH - dialog_width) // 2,
            (SCREEN_HEIGHT - dialog_height) // 2,
            dialog_width, dialog_height
        )
        pygame.draw.rect(screen, WHITE, dialog_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2, border_radius=10)

        text_surf = FONT.render("Promote to:", True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 30))
        screen.blit(text_surf, text_rect)

        pieces_to_promote = ['q', 'r', 'b', 'n']
        for i, piece_char in enumerate(pieces_to_promote):
            symbol = piece_char.upper() if self.game.to_move == "black" else piece_char
            img = self.piece_images.get(symbol)
            if img:
                img_rect = img.get_rect(
                    center=(
                        dialog_rect.left + (i + 1) * dialog_width // 5,
                        dialog_rect.bottom - 60
                    )
                )
                screen.blit(img, img_rect)
                
    def handle_promotion_click(self, pos):
        dialog_rect = pygame.Rect(
            (SCREEN_WIDTH - 400) // 2,
            (SCREEN_HEIGHT - 200) // 2,
            400, 200
        )
        
        pieces_to_promote = ['q', 'r', 'b', 'n']
        for i, piece_char in enumerate(pieces_to_promote):
            img_rect = pygame.Rect(
                dialog_rect.left + (i + 1) * 400 // 5 - SQUARE_SIZE // 2,
                dialog_rect.bottom - 60 - SQUARE_SIZE // 2,
                SQUARE_SIZE, SQUARE_SIZE
            )
            
            x, y = pygame.mouse.get_pos()
            if img_rect.collidepoint(x, y):
                self.game.make_move(
                    self.promotion_move,
                    self.promotion_move,
                    promo_piece=piece_char
                )
                self.promoting = False
                self.promotion_move = None
                self.game_over_text = self.game.outcome()
                if self.game_over_text and self.sound_on:
                    self.sound_checkmate.play()
                return

    def draw_sidebar(self):
        sidebar_rect = pygame.Rect(BOARD_SIZE_PX, 0, SCREEN_WIDTH - BOARD_SIZE_PX, SCREEN_HEIGHT)
        pygame.draw.rect(screen, BACKGROUND_COLOR, sidebar_rect)

        title_text = BOLD_FONT.render("Game Stats", True, WHITE)
        title_rect = title_text.get_rect(center=(
            (BOARD_SIZE_PX + SCREEN_WIDTH) // 2,
            50
        ))
        screen.blit(title_text, title_rect)
        
        self.draw_captured_pieces()
        self.draw_moves_history()
        
    def draw_captured_pieces(self):
        white_captures_text = BOLD_FONT.render("White Captured", True, BAR_BLACK)
        screen.blit(white_captures_text, (BOARD_SIZE_PX + 20, 100))
        
        y_offset = 130
        for i, piece in enumerate(self.game.captured_pieces["black"]):
            img = self.piece_images.get(piece.symbol)
            if img:
                scaled_img = pygame.transform.scale(img, (SQUARE_SIZE // 2, SQUARE_SIZE // 2))
                screen.blit(scaled_img, (
                    BOARD_SIZE_PX + 20 + (i % 8) * (SQUARE_SIZE // 2 + 5),
                    y_offset + (i // 8) * (SQUARE_SIZE // 2 + 5)
                ))
                
        black_captures_text = BOLD_FONT.render("Black Captured", True, BAR_WHITE)
        screen.blit(black_captures_text, (BOARD_SIZE_PX + 20, 250))
        
        y_offset = 280
        for i, piece in enumerate(self.game.captured_pieces["white"]):
            img = self.piece_images.get(piece.symbol)
            if img:
                scaled_img = pygame.transform.scale(img, (SQUARE_SIZE // 2, SQUARE_SIZE // 2))
                screen.blit(scaled_img, (
                    BOARD_SIZE_PX + 20 + (i % 8) * (SQUARE_SIZE // 2 + 5),
                    y_offset + (i // 8) * (SQUARE_SIZE // 2 + 5)
                ))

    def draw_moves_history(self):
        history_text = BOLD_FONT.render("Moves", True, WHITE)
        screen.blit(history_text, (BOARD_SIZE_PX + 20, 400))
        
        y_offset = 430
        for i, move in enumerate(self.game.full_move_history):
            text = FONT.render(move, True, WHITE)
            screen.blit(text, (BOARD_SIZE_PX + 20, y_offset + i * 25))

    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event)

            if self.game_mode == "Start":
                self.draw_start_menu()
            elif self.game_mode == "Lessons":
                self.draw_lessons_menu()
            elif self.game_mode == "LessonContent":
                self.draw_lesson_screen()
            elif self.game_mode == "Game":
                screen.fill(BACKGROUND_COLOR)
                self.draw_board()
                self.draw_pieces()
                self.draw_coords()
                self.draw_sidebar()
                if self.promoting:
                    self.draw_promotion_dialog()
                if self.game_over_text:
                    self.draw_game_over()
                pygame.display.flip()

        pygame.quit()
        sys.exit()
if __name__ == "__main__":
    game = Game()
    gui = ChessGUI(game)
    gui.run()