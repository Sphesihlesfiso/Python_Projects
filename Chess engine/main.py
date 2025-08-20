import pygame
import sys
import os
import random
from typing import List, Tuple, Dict, Optional, Any

pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BOARD_SIZE_PX = 800
BOARD_SIZE = 8
SQUARE_SIZE = BOARD_SIZE_PX // BOARD_SIZE
FPS = 60

# Colors
WHITE = (238, 238, 210)
BLACK = (118, 150, 86)
BACKGROUND_COLOR = (49, 46, 43)
HIGHLIGHT = (255, 255, 0)
CHECK_RED = (255, 0, 0)
MOVE_HIGHLIGHT = (0, 0, 0, 50)
BUTTON_COLOR = (60, 60, 60)
BUTTON_HOVER_COLOR = (80, 80, 80)
TEXT_COLOR = (255, 255, 255)
COORD_COLOR = (128, 128, 128)
BAR_BLACK = (200, 200, 200)
BAR_WHITE = (50, 50, 50)

# Fonts
pygame.font.init()
FONT_SIZE_NORMAL = 24
FONT_SIZE_LARGE = 48
FONT_SIZE_BOLD = 32
FONT = pygame.font.SysFont('Arial', FONT_SIZE_NORMAL)
LARGE_FONT = pygame.font.SysFont('Arial', FONT_SIZE_LARGE, bold=True)
BOLD_FONT = pygame.font.SysFont('Arial', FONT_SIZE_BOLD, bold=True)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Engine")
clock = pygame.time.Clock()

Position = Tuple[int, int]
PieceSymbol = str

COL_TO_FILE = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
FILE_TO_COL = {v: k for k, v in COL_TO_FILE.items()}

# Lessons content
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

# Piece base class
class Piece:
    def __init__(self, row: int, col: int, color: str, symbol: PieceSymbol, value: int):
        self.row = row
        self.col = col
        self.color = color
        self.symbol = symbol
        self.value = value
        self.has_moved = False

    def pos(self) -> Position:
        return (self.row, self.col)

    def is_valid_move(self, end_pos: Position, board) -> bool:
        raise NotImplementedError

    def get_possible_moves(self, board) -> List[Position]:
        raise NotImplementedError

    def get_possible_move_vectors(self):
        raise NotImplementedError
    
    def __repr__(self) -> str:
        return f"{self.color.capitalize()} {self.__class__.__name__} at ({self.row}, {self.col})"

# Piece subclasses
class King(Piece):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color, 'K' if color == "white" else 'k', 1000)

    def get_possible_move_vectors(self):
        return [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def get_possible_moves(self, board):
        moves = []
        for dr, dc in self.get_possible_move_vectors():
            end_row, end_col = self.row + dr, self.col + dc
            if 1 <= end_row <= 8 and 1 <= end_col <= 8:
                end_piece = board.piece_at((end_row, end_col))
                if end_piece is None or end_piece.color != self.color:
                    moves.append((end_row, end_col))

        # Castling
        if not self.has_moved and not board.in_check(self.color):
            # Kingside castling
            rook_pos = (self.row, 8)
            rook = board.piece_at(rook_pos)
            if isinstance(rook, Rook) and not rook.has_moved:
                path_empty = True
                for c in range(self.col + 1, rook_pos[1]):
                    if board.piece_at((self.row, c)):
                        path_empty = False
                        break
                if path_empty:
                    # Check squares the king moves through
                    if not board.is_attacked((self.row, self.col + 1), self.color) and not board.is_attacked((self.row, self.col + 2), self.color):
                        moves.append((self.row, self.col + 2))
            
            # Queenside castling
            rook_pos = (self.row, 1)
            rook = board.piece_at(rook_pos)
            if isinstance(rook, Rook) and not rook.has_moved:
                path_empty = True
                for c in range(self.col - 1, rook_pos[1], -1):
                    if board.piece_at((self.row, c)):
                        path_empty = False
                        break
                if path_empty:
                    if not board.is_attacked((self.row, self.col - 1), self.color) and not board.is_attacked((self.row, self.col - 2), self.color):
                        moves.append((self.row, self.col - 2))

        return moves

class Queen(Piece):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color, 'Q' if color == "white" else 'q', 9)

    def get_possible_move_vectors(self):
        return [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

    def get_possible_moves(self, board):
        moves = []
        for dr, dc in self.get_possible_move_vectors():
            for i in range(1, 8):
                end_row, end_col = self.row + dr * i, self.col + dc * i
                if not (1 <= end_row <= 8 and 1 <= end_col <= 8):
                    break
                
                end_piece = board.piece_at((end_row, end_col))
                if end_piece is None:
                    moves.append((end_row, end_col))
                else:
                    if end_piece.color != self.color:
                        moves.append((end_row, end_col))
                    break
        return moves

class Rook(Piece):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color, 'R' if color == "white" else 'r', 5)

    def get_possible_move_vectors(self):
        return [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
    def get_possible_moves(self, board):
        moves = []
        for dr, dc in self.get_possible_move_vectors():
            for i in range(1, 8):
                end_row, end_col = self.row + dr * i, self.col + dc * i
                if not (1 <= end_row <= 8 and 1 <= end_col <= 8):
                    break
                
                end_piece = board.piece_at((end_row, end_col))
                if end_piece is None:
                    moves.append((end_row, end_col))
                else:
                    if end_piece.color != self.color:
                        moves.append((end_row, end_col))
                    break
        return moves

class Bishop(Piece):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color, 'B' if color == "white" else 'b', 3)

    def get_possible_move_vectors(self):
        return [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def get_possible_moves(self, board):
        moves = []
        for dr, dc in self.get_possible_move_vectors():
            for i in range(1, 8):
                end_row, end_col = self.row + dr * i, self.col + dc * i
                if not (1 <= end_row <= 8 and 1 <= end_col <= 8):
                    break
                
                end_piece = board.piece_at((end_row, end_col))
                if end_piece is None:
                    moves.append((end_row, end_col))
                else:
                    if end_piece.color != self.color:
                        moves.append((end_row, end_col))
                    break
        return moves

class Knight(Piece):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color, 'N' if color == "white" else 'n', 3)

    def get_possible_move_vectors(self):
        return [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

    def get_possible_moves(self, board):
        moves = []
        for dr, dc in self.get_possible_move_vectors():
            end_row, end_col = self.row + dr, self.col + dc
            if 1 <= end_row <= 8 and 1 <= end_col <= 8:
                end_piece = board.piece_at((end_row, end_col))
                if end_piece is None or end_piece.color != self.color:
                    moves.append((end_row, end_col))
        return moves

class Pawn(Piece):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color, 'P' if color == "white" else 'p', 1)
        self.direction = 1 if color == "white" else -1

    def get_possible_moves(self, board):
        moves = []
        # Normal move
        end_row = self.row + self.direction
        if 1 <= end_row <= 8:
            if board.piece_at((end_row, self.col)) is None:
                moves.append((end_row, self.col))
                # Initial two-square move
                if not self.has_moved:
                    end_row_two = self.row + 2 * self.direction
                    if board.piece_at((end_row_two, self.col)) is None:
                        moves.append((end_row_two, self.col))

        # Captures
        for dc in [-1, 1]:
            end_row, end_col = self.row + self.direction, self.col + dc
            if 1 <= end_row <= 8 and 1 <= end_col <= 8:
                end_piece = board.piece_at((end_row, end_col))
                if end_piece and end_piece.color != self.color:
                    moves.append((end_row, end_col))
        
        # En passant
        en_passant_target = board.en_passant_target
        if en_passant_target:
            if en_passant_target[0] == self.row + self.direction and abs(en_passant_target[1] - self.col) == 1:
                moves.append(en_passant_target)

        return moves

class Game:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.pieces = []
        self.board = {}
        self.to_move = "white"
        self.en_passant_target: Optional[Position] = None
        self.captured_pieces: Dict[str, List[Piece]] = {"white": [], "black": []}
        self.kings: Dict[str, Optional[King]] = {"white": None, "black": None}
        self.setup_board()
    
    def get_score(self) -> int:
        score_white = sum(p.value for p in self.captured_pieces["black"])
        score_black = sum(p.value for p in self.captured_pieces["white"])
        return score_white - score_black

    def setup_board(self):
        # White pieces
        self.add_piece(Rook(1, 1, "white"))
        self.add_piece(Knight(1, 2, "white"))
        self.add_piece(Bishop(1, 3, "white"))
        self.add_piece(Queen(1, 4, "white"))
        self.kings["white"] = King(1, 5, "white")
        self.add_piece(self.kings["white"])
        self.add_piece(Bishop(1, 6, "white"))
        self.add_piece(Knight(1, 7, "white"))
        self.add_piece(Rook(1, 8, "white"))
        for c in range(1, 9):
            self.add_piece(Pawn(2, c, "white"))

        # Black pieces
        self.add_piece(Rook(8, 1, "black"))
        self.add_piece(Knight(8, 2, "black"))
        self.add_piece(Bishop(8, 3, "black"))
        self.add_piece(Queen(8, 4, "black"))
        self.kings["black"] = King(8, 5, "black")
        self.add_piece(self.kings["black"])
        self.add_piece(Bishop(8, 6, "black"))
        self.add_piece(Knight(8, 7, "black"))
        self.add_piece(Rook(8, 8, "black"))
        for c in range(1, 9):
            self.add_piece(Pawn(7, c, "black"))

    def add_piece(self, piece: Piece):
        self.pieces.append(piece)
        self.board[piece.pos()] = piece

    def piece_at(self, pos: Position) -> Optional[Piece]:
        return self.board.get(pos)

    def move_piece(self, start_pos: Position, end_pos: Position):
        piece = self.piece_at(start_pos)
        if not piece:
            return

        captured_piece = self.piece_at(end_pos)
        if captured_piece:
            self.pieces.remove(captured_piece)
            self.captured_pieces[piece.color].append(captured_piece)

        del self.board[start_pos]
        piece.row, piece.col = end_pos
        self.board[end_pos] = piece
        piece.has_moved = True
        
    def in_check(self, color: str) -> bool:
        king = self.kings[color]
        if not king: return False
        return self.is_attacked(king.pos(), color)

    def is_attacked(self, pos: Position, by_color: str) -> bool:
        opponent_color = "white" if by_color == "black" else "black"
        for piece in self.pieces:
            if piece.color == opponent_color:
                if isinstance(piece, Pawn):
                    direction = 1 if piece.color == "white" else -1
                    if (piece.row + direction, piece.col - 1) == pos or \
                       (piece.row + direction, piece.col + 1) == pos:
                        return True
                elif isinstance(piece, Knight):
                    for dr, dc in piece.get_possible_move_vectors():
                        if (piece.row + dr, piece.col + dc) == pos:
                            return True
                elif isinstance(piece, King):
                    for dr, dc in piece.get_possible_move_vectors():
                        if (piece.row + dr, piece.col + dc) == pos:
                            return True
                else: # Rook, Bishop, Queen
                    for dr, dc in piece.get_possible_move_vectors():
                        for i in range(1, 8):
                            end_row, end_col = piece.row + dr * i, piece.col + dc * i
                            if not (1 <= end_row <= 8 and 1 <= end_col <= 8):
                                break
                            
                            end_piece = self.piece_at((end_row, end_col))
                            if (end_row, end_col) == pos:
                                return True
                            if end_piece:
                                break
        return False
    
    def legal_moves_for(self, piece: Piece) -> List[Position]:
        moves = []
        possible_moves = piece.get_possible_moves(self)
        
        for end_pos in possible_moves:
            temp_game = self.copy()
            temp_game.make_move(piece.pos(), end_pos, dry_run=True)
            if not temp_game.in_check(piece.color):
                moves.append(end_pos)
        return moves

    def get_all_legal_moves(self, color: str) -> Dict[Position, List[Position]]:
        all_moves = {}
        for piece in self.pieces:
            if piece.color == color:
                legal_moves = self.legal_moves_for(piece)
                if legal_moves:
                    all_moves[piece.pos()] = legal_moves
        return all_moves

    def is_game_over(self) -> bool:
        return self.outcome() is not None

    def outcome(self) -> Optional[str]:
        if not self.get_all_legal_moves(self.to_move):
            if self.in_check(self.to_move):
                return f"Checkmate! {'White' if self.to_move == 'black' else 'Black'} wins!"
            else:
                return "Stalemate!"
        return None
    
    def copy(self):
        new_game = Game()
        new_game.pieces = [
            type(p)(p.row, p.col, p.color) 
            if not isinstance(p, (King, Queen, Rook, Bishop, Knight, Pawn)) else p
            for p in self.pieces
        ]
        new_game.board = {p.pos(): p for p in new_game.pieces}
        new_game.to_move = self.to_move
        new_game.captured_pieces = {
            "white": [
                type(p)(p.row, p.col, p.color) for p in self.captured_pieces["white"]
            ],
            "black": [
                type(p)(p.row, p.col, p.color) for p in self.captured_pieces["black"]
            ],
        }
        return new_game

    def make_move(self, start_pos: Position, end_pos: Position, dry_run: bool = False, promo_piece: Optional[str] = None) -> bool:
        piece = self.piece_at(start_pos)
        if not piece or piece.color != self.to_move:
            return False

        
            
        if not dry_run:
            self.en_passant_target = None
            
            # Pawn promotion
            if isinstance(piece, Pawn) and (end_pos[0] == 1 or end_pos[0] == 8):
                if not promo_piece:
                    return False
                
                new_piece: Optional[Piece] = None
                if promo_piece.lower() == 'q':
                    new_piece = Queen(piece.row, piece.col, piece.color)
                elif promo_piece.lower() == 'r':
                    new_piece = Rook(piece.row, piece.col, piece.color)
                elif promo_piece.lower() == 'b':
                    new_piece = Bishop(piece.row, piece.col, piece.color)
                elif promo_piece.lower() == 'n':
                    new_piece = Knight(piece.row, piece.col, piece.color)
                
                if new_piece:
                    self.pieces.remove(piece)
                    del self.board[piece.pos()]
                    new_piece.row, new_piece.col = end_pos
                    self.add_piece(new_piece)
                
            # Castling
            if isinstance(piece, King) and abs(start_pos[1] - end_pos[1]) == 2:
                if end_pos[1] == 7: # Kingside
                    rook_start, rook_end = (start_pos[0], 8), (start_pos[0], 6)
                else: # Queenside
                    rook_start, rook_end = (start_pos[0], 1), (start_pos[0], 4)
                self.move_piece(rook_start, rook_end)
            
            # En passant
            elif isinstance(piece, Pawn) and end_pos == self.en_passant_target:
                captured_pos = (start_pos[0], end_pos[1])
                captured_piece = self.piece_at(captured_pos)
                if captured_piece:
                    self.pieces.remove(captured_piece)
                    self.captured_pieces[piece.color].append(captured_piece)
                    del self.board[captured_pos]
            
            # Set en passant target
            if isinstance(piece, Pawn) and abs(start_pos[0] - end_pos[0]) == 2:
                self.en_passant_target = (start_pos[0] + piece.direction, start_pos[1])
                
            self.move_piece(start_pos, end_pos)
            self.to_move = "black" if self.to_move == "white" else "white"

        return True

class AIOpponent:
    def __init__(self, game):
        self.game = game

    def make_move(self):
        legal_moves = self.game.get_all_legal_moves("black")
        if not legal_moves:
            return False
            
        start_pos = random.choice(list(legal_moves.keys()))
        end_pos = random.choice(legal_moves[start_pos])

        return self.game.make_move(start_pos, end_pos)

class ChessGUI:
    def __init__(self, game, ai_opponent):
        self.game = game
        self.ai_opponent = ai_opponent
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

        if self.game.to_move != "white":
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
            symbol = piece_char.upper() if self.game.to_move == "white" else piece_char
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
        
        self.draw_score()
        self.draw_captured_pieces()
        
    def draw_score(self):
        score = self.game.get_score()
        score_text = f"Score: {'+' if score > 0 else ''}{score}"
        
        score_surf = BOLD_FONT.render(score_text, True, WHITE)
        score_rect = score_surf.get_rect(center=((BOARD_SIZE_PX + SCREEN_WIDTH) // 2, 100))
        screen.blit(score_surf, score_rect)

    def draw_captured_pieces(self):
        white_captures_text = BOLD_FONT.render("White Captured", True, BAR_BLACK)
        screen.blit(white_captures_text, (BOARD_SIZE_PX + 20, 150))
        
        y_offset = 180
        for i, piece in enumerate(self.game.captured_pieces["black"]):
            img = self.piece_images.get(piece.symbol)
            if img:
                scaled_img = pygame.transform.scale(img, (SQUARE_SIZE // 2, SQUARE_SIZE // 2))
                screen.blit(scaled_img, (
                    BOARD_SIZE_PX + 20 + (i % 8) * (SQUARE_SIZE // 2 + 5),
                    y_offset + (i // 8) * (SQUARE_SIZE // 2 + 5)
                ))
                
        black_captures_text = BOLD_FONT.render("Black Captured", True, BAR_WHITE)
        screen.blit(black_captures_text, (BOARD_SIZE_PX + 20, 300))
        
        y_offset = 330
        for i, piece in enumerate(self.game.captured_pieces["white"]):
            img = self.piece_images.get(piece.symbol)
            if img:
                scaled_img = pygame.transform.scale(img, (SQUARE_SIZE // 2, SQUARE_SIZE // 2))
                screen.blit(scaled_img, (
                    BOARD_SIZE_PX + 20 + (i % 8) * (SQUARE_SIZE // 2 + 5),
                    y_offset + (i // 8) * (SQUARE_SIZE // 2 + 5)
                ))

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
                # Check for AI move
                if self.game.to_move == "black" and not self.game_over_text:
                    if self.ai_opponent.make_move():
                        if self.sound_on:
                            if self.game.in_check("white"):
                                self.sound_check.play()
                            else:
                                self.sound_move.play()
                        
                        self.game_over_text = self.game.outcome()
                        if self.game_over_text:
                            if self.sound_on:
                                self.sound_game_over.play()

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

def main():
    game = Game()
    ai_opponent = AIOpponent(game)
    gui = ChessGUI(game, ai_opponent)
    gui.run()

if __name__ == "__main__":
    main()