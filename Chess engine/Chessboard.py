# A fully playable chess game with a start menu, an AI opponent, and a stats sidebar.
# This version includes fixes for the screen width and the accuracy of captured pieces.
# Features: legal move validation, captures, check, checkmate, stalemate, castling, en passant, promotion.
# The AI uses a simple Minimax algorithm with a depth of 2.

from typing import List, Tuple, Dict, Optional
import pygame
import os
import array
import random
import sys

# Initialize pygame and its mixer for sound
pygame.init()
pygame.mixer.init()

# --- CONSTANTS ---
# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700  # Updated screen width
# Board dimensions
BOARD_SIZE_PX = 600
BOARD_SIZE = 8
SQUARE_SIZE = BOARD_SIZE_PX // BOARD_SIZE
FPS = 60

# Colors
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (247, 247, 105, 150)
MOVE_HIGHLIGHT = (106, 168, 79, 150)
CHECK_RED = (255, 0, 0, 150)
COORD_COLOR = (100, 100, 100)
TEXT_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (240, 240, 240)
BAR_WHITE = (255, 255, 255)
BAR_BLACK = (50, 50, 50)
BUTTON_COLOR = (150, 200, 255)
BUTTON_HOVER_COLOR = (100, 150, 200)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
LARGE_FONT = pygame.font.SysFont('Arial', 48)
BOLD_FONT = pygame.font.SysFont('Arial', 28, bold=True)
PIECE_FONT = pygame.font.SysFont('Arial', 40)

# Screen setup - now a global variable to be passed to the GUI
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# --- GUI CLASS ---
class ChessGUI:
    def __init__(self, game):
        self.game = game
        self.selected = None
        self.valid_moves = []
        self.promoting = False
        self.promotion_move = None
        self.game_over_text = None
        self.game_mode = None # "AI" or "Player"
        self.sound_on = True
        
        # Generate a simple 'click' sound effect programmatically
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
            
    def _piece_name(self, symbol):
        """Returns the full name of a piece based on its symbol."""
        symbol = symbol.lower()
        if symbol == 'p': return 'Pawn'
        if symbol == 'n': return 'Knight'
        if symbol == 'b': return 'Bishop'
        if symbol == 'r': return 'Rook'
        if symbol == 'q': return 'Queen'
        if symbol == 'k': return 'King'
        return ' '
        
    def draw_menu(self):
        """Draws the start-up menu with game mode options."""
        screen.fill(BACKGROUND_COLOR)
        
        title_text = LARGE_FONT.render("Pygame Chess", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        ai_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        player_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw AI button
        ai_color = BUTTON_HOVER_COLOR if ai_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, ai_color, ai_button_rect, border_radius=10)
        ai_text = FONT.render("Play vs. AI", True, TEXT_COLOR)
        ai_text_rect = ai_text.get_rect(center=ai_button_rect.center)
        screen.blit(ai_text, ai_text_rect)
        
        # Draw Player button
        player_color = BUTTON_HOVER_COLOR if player_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, player_color, player_button_rect, border_radius=10)
        player_text = FONT.render("Play vs. Player", True, TEXT_COLOR)
        player_text_rect = player_text.get_rect(center=player_button_rect.center)
        screen.blit(player_text, player_text_rect)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ai_button_rect.collidepoint(event.pos):
                    self.game_mode = "AI"
                    return True
                if player_button_rect.collidepoint(event.pos):
                    self.game_mode = "Player"
                    return True
        return False

    def draw_board(self):
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
            row, col = self.selected[0] - 1, self.selected[1] - 1
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(HIGHLIGHT)
            screen.blit(s, (board_offset_x + col * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row - 1) * SQUARE_SIZE))
        
        # Highlight valid moves
        for move in self.valid_moves:
            row, col = move[0] - 1, move[1] - 1
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(MOVE_HIGHLIGHT)
            screen.blit(s, (board_offset_x + col * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row - 1) * SQUARE_SIZE))
        
        # Highlight king in check
        king_pos = self.game.kings.get(self.game.to_move)
        if king_pos and self.game.in_check(self.game.to_move):
            row, col = king_pos.pos()[0] - 1, king_pos.pos()[1] - 1
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill(CHECK_RED)
            screen.blit(s, (board_offset_x + col * SQUARE_SIZE, board_offset_y + (BOARD_SIZE - row - 1) * SQUARE_SIZE))
        
        # Draw pieces with text instead of images
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece_symbol = self.game.board.array[row][col]
                if piece_symbol != " ":
                    text_color = (0, 0, 0) if piece_symbol.islower() else (255, 255, 255)
                    text_surf = PIECE_FONT.render(piece_symbol.upper(), True, text_color)
                    text_rect = text_surf.get_rect(center=(board_offset_x + col * SQUARE_SIZE + SQUARE_SIZE // 2, board_offset_y + (BOARD_SIZE - row - 1) * SQUARE_SIZE + SQUARE_SIZE // 2))
                    screen.blit(text_surf, text_rect)
        
        # Draw promotion menu if needed
        if self.promoting:
            self.draw_promotion_menu(board_offset_x, board_offset_y)
        
    def draw_sidebar(self):
        """Draws game stats, captured pieces, and a material advantage bar."""
        # Position sidebar on the right
        sidebar_x = (SCREEN_WIDTH + BOARD_SIZE_PX) // 2 + 30
        y_offset = 30
        
        # --- Stats Container ---
        stats_width = 250
        stats_height = 640
        stats_rect = pygame.Rect(sidebar_x, y_offset, stats_width, stats_height)
        pygame.draw.rect(screen, (220, 220, 220), stats_rect)
        pygame.draw.rect(screen, (100, 100, 100), stats_rect, 2)
        
        y_offset_in_box = 20
        content_x = sidebar_x + 20

        # --- White Player Stats ---
        text_white_title = BOLD_FONT.render("White Player", True, TEXT_COLOR)
        screen.blit(text_white_title, (content_x, y_offset + y_offset_in_box))
        y_offset_in_box += 40

        white_score = sum(self.game.piece_value(p) for p in self.game.captured_pieces["black"])
        text_white_score = FONT.render(f"Score: {white_score}", True, TEXT_COLOR)
        screen.blit(text_white_score, (content_x, y_offset + y_offset_in_box))
        y_offset_in_box += 30

        text_white_captured = FONT.render("Captured Pieces:", True, TEXT_COLOR)
        screen.blit(text_white_captured, (content_x, y_offset + y_offset_in_box))
        y_offset_in_box += 30
        
        # Display captured pieces for white
        for i, piece in enumerate(self.game.captured_pieces["black"]):
            piece_name = self._piece_name(piece.symbol)
            text_surf = FONT.render(piece_name, True, TEXT_COLOR)
            screen.blit(text_surf, (content_x, y_offset + y_offset_in_box + i * 30))
        y_offset_in_box += max(len(self.game.captured_pieces["black"]) * 30 + 30, 60) # Ensure a minimum gap

        # --- Black Player Stats ---
        text_black_title = BOLD_FONT.render("Black Player", True, TEXT_COLOR)
        screen.blit(text_black_title, (content_x, y_offset + y_offset_in_box))
        y_offset_in_box += 40

        black_score = sum(self.game.piece_value(p) for p in self.game.captured_pieces["white"])
        text_black_score = FONT.render(f"Score: {black_score}", True, TEXT_COLOR)
        screen.blit(text_black_score, (content_x, y_offset + y_offset_in_box))
        y_offset_in_box += 30

        text_black_captured = FONT.render("Captured Pieces:", True, TEXT_COLOR)
        screen.blit(text_black_captured, (content_x, y_offset + y_offset_in_box))
        y_offset_in_box += 30
        
        # Display captured pieces for black
        for i, piece in enumerate(self.game.captured_pieces["white"]):
            piece_name = self._piece_name(piece.symbol)
            text_surf = FONT.render(piece_name, True, TEXT_COLOR)
            screen.blit(text_surf, (content_x, y_offset + y_offset_in_box + i * 30))
        y_offset_in_box += max(len(self.game.captured_pieces["white"]) * 30 + 30, 60) # Ensure a minimum gap

        # --- Material Advantage Bar ---
        bar_height = 20
        total_score = white_score + black_score
        
        # Ensure total_score is not zero to prevent division by zero
        if total_score == 0:
            white_percentage = 50
        else:
            white_percentage = (white_score / total_score) * 100
        
        bar_y = y_offset + y_offset_in_box + 20
        bar_rect = pygame.Rect(content_x, bar_y, stats_width - 40, bar_height)
        pygame.draw.rect(screen, BAR_BLACK, bar_rect)
        white_bar_width = int((bar_rect.width / 100) * white_percentage)
        pygame.draw.rect(screen, BAR_WHITE, pygame.Rect(bar_rect.x, bar_y, white_bar_width, bar_height))
        pygame.draw.rect(screen, TEXT_COLOR, bar_rect, 1)

        # Draw a percentage indicator on the bar
        percentage_text = FONT.render(f"{white_percentage:.0f}%", True, TEXT_COLOR)
        screen.blit(percentage_text, (bar_rect.x + bar_rect.width // 2 - percentage_text.get_width() // 2, bar_rect.y + bar_height + 5))
        y_offset_in_box += bar_height + 40

        # --- Status Text ---
        status = f"Turn {self.game.move_number} - {self.game.to_move.capitalize()}'s turn"
        if self.game.in_check(self.game.to_move):
            status += " (CHECK)"
        text = FONT.render(status, True, TEXT_COLOR)
        screen.blit(text, (content_x, y_offset + stats_height - 60))

        # --- Sound Toggle Button ---
        sound_text = "Sound: ON" if self.sound_on else "Sound: OFF"
        self.sound_button_rect = pygame.Rect(content_x, y_offset + stats_height - 30, stats_width - 40, 30)
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER_COLOR if self.sound_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, self.sound_button_rect, border_radius=5)
        sound_text_surf = FONT.render(sound_text, True, TEXT_COLOR)
        sound_text_rect = sound_text_surf.get_rect(center=self.sound_button_rect.center)
        screen.blit(sound_text_surf, sound_text_rect)


    def draw_promotion_menu(self, board_offset_x, board_offset_y):
        """Draws the promotion selection menu."""
        s = pygame.Surface((BOARD_SIZE_PX, BOARD_SIZE_PX), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (board_offset_x, board_offset_y))
        
        color = self.game.to_move
        pieces = ['Q', 'R', 'B', 'N'] if color == "white" else ['q', 'r', 'b', 'n']
        text = LARGE_FONT.render("Promote to:", True, (255, 255, 255))
        screen.blit(text, (board_offset_x + BOARD_SIZE_PX//2 - text.get_width()//2, board_offset_y + BOARD_SIZE_PX//2 - 100))
        
        for i, piece in enumerate(pieces):
            rect = pygame.Rect(board_offset_x + BOARD_SIZE_PX//2 - 200 + i*100, board_offset_y + BOARD_SIZE_PX//2, 80, 80)
            pygame.draw.rect(screen, (255, 255, 255), rect)
            text_surf = PIECE_FONT.render(piece.upper(), True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=(board_offset_x + BOARD_SIZE_PX//2 - 200 + i*100 + 40, board_offset_y + BOARD_SIZE_PX//2 + 40))
            screen.blit(text_surf, text_rect)
            
    def handle_click(self, pos):
        """Handles mouse clicks for piece selection and movement."""
        # Use the new board offset
        board_offset_x = (SCREEN_WIDTH - BOARD_SIZE_PX) // 2
        board_offset_y = (SCREEN_HEIGHT - BOARD_SIZE_PX) // 2
        
        # Handle sound toggle button click
        if hasattr(self, 'sound_button_rect') and self.sound_button_rect.collidepoint(pos):
            self.sound_on = not self.sound_on
            return

        # Handle "Play Again" button click if game is over
        if self.game_over_text:
            if hasattr(self, 'play_again_rect') and self.play_again_rect.collidepoint(pos):
                self.game.reset_game()
                self.game_over_text = None
                self.selected = None
                self.valid_moves = []
                self.game_mode = None
                return

        # Don't allow moves if game is over
        if self.game_over_text:
            return

        # Check if the click is on the board
        if not (board_offset_x <= pos[0] <= board_offset_x + BOARD_SIZE_PX and board_offset_y <= pos[1] <= board_offset_y + BOARD_SIZE_PX):
            self.selected = None
            self.valid_moves = []
            return

        col = (pos[0] - board_offset_x) // SQUARE_SIZE
        row = BOARD_SIZE - ((pos[1] - board_offset_y) // SQUARE_SIZE)
        
        if self.promoting:
            self.handle_promotion_click(pos, board_offset_x, board_offset_y)
            return
        
        clicked_pos = (row, col + 1)
        clicked_piece = self.game.piece_at(clicked_pos)
        
        if self.selected:
            if clicked_pos in self.valid_moves:
                piece_to_move = self.game.piece_at(self.selected)
                if isinstance(piece_to_move, Pawn) and (row == 8 or row == 1):
                    self.promoting = True
                    self.promotion_move = clicked_pos
                else:
                    if self.game.make_move(self.selected, clicked_pos):
                        if self.sound_on:
                            self.move_sound.play()
                    self.selected = None
                    self.valid_moves = []
            else:
                self.selected = None
                self.valid_moves = []
        
        if clicked_piece and clicked_piece.color == self.game.to_move:
            self.selected = clicked_pos
            self.valid_moves = self.game.legal_moves_for(clicked_piece)

    def handle_promotion_click(self, pos, board_offset_x, board_offset_y):
        """Handles clicks on the promotion menu."""
        if (board_offset_y + BOARD_SIZE_PX // 2) <= pos[1] <= (board_offset_y + BOARD_SIZE_PX // 2 + 80):
            for i in range(4):
                if (board_offset_x + BOARD_SIZE_PX // 2 - 200 + i*100) <= pos[0] <= (board_offset_x + BOARD_SIZE_PX // 2 - 200 + i*100 + 80):
                    pieces = ['Q', 'R', 'B', 'N']
                    if self.game.make_move(self.selected, self.promotion_move, pieces[i]):
                        if self.sound_on:
                            self.move_sound.play()
                    self.promoting = False
                    self.selected = None
                    self.valid_moves = []
                    break
    
    def run(self):
        """Main game loop."""
        # Main menu loop
        while self.game_mode is None:
            self.draw_menu()
            
        running = True
        while running:
            # AI turn handling
            if self.game_mode == "AI" and self.game.to_move == "black" and not self.game.outcome():
                # Add a short delay to make the AI's move more noticeable
                pygame.time.wait(500) 
                self.game.ai_move()
                if self.sound_on:
                    self.move_sound.play()
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Fix: Handle clicks based on game mode and turn
                    if self.game_mode == "Player" or (self.game_mode == "AI" and self.game.to_move == "white"):
                        if event.button == 1:
                            self.handle_click(event.pos)
            
            screen.fill(BACKGROUND_COLOR)
            self.draw_board()
            self.draw_sidebar()
            
            outcome = self.game.outcome()
            if outcome:
                self.show_game_over(outcome)
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

    def show_game_over(self, outcome):
        """Displays game over message and a 'Play Again' button."""
        self.game_over_text = outcome
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, (0, 0))
        
        # Game over text
        text = LARGE_FONT.render(self.game_over_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)
        
        # Play Again button
        self.play_again_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER_COLOR if self.play_again_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, self.play_again_rect, border_radius=10)
        play_again_text = FONT.render("Play Again", True, TEXT_COLOR)
        play_again_text_rect = play_again_text.get_rect(center=self.play_again_rect.center)
        screen.blit(play_again_text, play_again_text_rect)

# --- BOARD CLASS ---
class Board:
    def __init__(self):
        self.array = [[" " for _ in range(8)] for _ in range(8)]

    def return_array(self) -> list:
        return self.array

    def Put_piece(self, r: int, c: int, piece: str):
        self.array[r-1][c-1] = piece

    def erase_x(self):
        for i in range(8):
            for j in range(8):
                if self.array[i][j] == "x":
                    self.array[i][j] = " "

# --- HELPERS ---
FILE_TO_COL = {c: i+1 for i, c in enumerate("abcdefgh")}
COL_TO_FILE = {v: k for k, v in FILE_TO_COL.items()}
Position = Tuple[int, int]

def in_bounds(r: int, c: int) -> bool:
    return 1 <= r <= 8 and 1 <= c <= 8

def algebraic_to_pos(s: str) -> Position:
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

    def pos(self) -> Position:
        return (self.row, self.col)

    def set_pos(self, r: int, c: int):
        self.row, self.col = r, c

    def is_enemy(self, board_array: List[List[str]], r: int, c: int) -> bool:
        ch = board_array[r-1][c-1]
        if ch == " ":
            return False
        return ch.islower() if self.color == "white" else ch.isupper()

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
    def gen_moves(self, game: "Game") -> List[Position]:
        arr = game.board.return_array()
        moves: List[Position] = []
        for dr, dc in self.DELTAS:
            r, c = self.row + dr, self.col + dc
            if in_bounds(r, c):
                ch = arr[r-1][c-1]
                if ch == " " or self.is_enemy(arr, r, c):
                    moves.append((r, c))
        if not self.moved and not game.in_check(self.color):
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

# --- GAME ENGINE CLASS ---
class Game:
    def __init__(self):
        self.board = Board()
        self.arr = self.board.return_array()
        self.to_move = "white"
        self.pieces: Dict[Position, Piece] = {}
        self.kings: Dict[str, King] = {}
        self.en_passant_target: Optional[Position] = None
        self.halfmove_clock = 0
        self.move_number = 1
        self.captured_pieces = {"white": [], "black": []}
        self._setup_startpos()
    
    def reset_game(self):
        self.board = Board()
        self.arr = self.board.return_array()
        self.to_move = "white"
        self.pieces = {}
        self.kings = {}
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.move_number = 1
        self.captured_pieces = {"white": [], "black": []}
        self._setup_startpos()

    def _place(self, p: Piece):
        self.pieces[p.pos()] = p
        r, c = p.pos()
        self.board.Put_piece(r, c, p.symbol)
        if isinstance(p, King):
            self.kings[p.color] = p

    def _setup_startpos(self):
        self.pieces.clear()
        self.kings.clear()
        # White pieces (rows 1-2)
        self._place(Rook(1,1,"white"))
        self._place(Knight(1,2,"white"))
        self._place(Bishop(1,3,"white"))
        self._place(Queen(1,4,"white"))
        self._place(King(1,5,"white"))
        self._place(Bishop(1,6,"white"))
        self._place(Knight(1,7,"white"))
        self._place(Rook(1,8,"white"))
        for c in range(1,9):
            self._place(Pawn(2,c,"white"))
        # Black pieces (rows 7-8)
        self._place(Rook(8,1,"black"))
        self._place(Knight(8,2,"black"))
        self._place(Bishop(8,3,"black"))
        self._place(Queen(8,4,"black"))
        self._place(King(8,5,"black"))
        self._place(Bishop(8,6,"black"))
        self._place(Knight(8,7,"black"))
        self._place(Rook(8,8,"black"))
        for c in range(1,9):
            self._place(Pawn(7,c,"black"))

    def piece_at(self, pos: Position) -> Optional[Piece]:
        return self.pieces.get(pos)

    def remove_at(self, pos: Position):
        p = self.pieces.pop(pos, None)
        if p is not None:
            r, c = pos
            self.board.Put_piece(r, c, " ")

    def move_piece_obj(self, p: Piece, dest: Position):
        self.remove_at(p.pos())
        if dest in self.pieces:
            self.remove_at(dest)
        p.set_pos(*dest)
        self.pieces[dest] = p
        r, c = dest
        self.board.Put_piece(r, c, p.symbol)
        p.moved = True

    def color_of(self, ch: str) -> Optional[str]:
        if ch == " ":
            return None
        return "white" if ch.isupper() else "black"

    def squares_attacked_by(self, color: str) -> set:
        attacked = set()
        for pos, p in self.pieces.items():
            if p.color != color:
                continue
            if isinstance(p, Pawn):
                dir = 1 if p.color == "white" else -1
                for dc in (-1, 1):
                    r, c = p.row + dir, p.col + dc
                    if in_bounds(r, c):
                        attacked.add((r, c))
            elif isinstance(p, King):
                for dr, dc in King.DELTAS:
                    r, c = p.row + dr, p.col + dc
                    if in_bounds(r, c):
                        attacked.add((r, c))
            elif isinstance(p, Knight):
                for dr, dc in Knight.DELTAS:
                    r, c = p.row + dr, p.col + dc
                    if in_bounds(r, c):
                        attacked.add((r, c))
            else:
                for dr, dc in p.directions:
                    r, c = p.row + dr, p.col + dc
                    while in_bounds(r, c):
                        attacked.add((r, c))
                        if self.arr[r-1][c-1] != " ":
                            break
                        r += dr
                        c += dc
        return attacked

    def in_check(self, color: str) -> bool:
        king = self.kings.get(color)
        if not king:
            return False
        enemy = "black" if color == "white" else "white"
        attacked = self.squares_attacked_by(enemy)
        return king.pos() in attacked

    def can_castle(self, color: str, king_side: bool) -> bool:
        king = self.kings[color]
        if king.moved:
            return False
        row = 1 if color == "white" else 8
        if king_side:
            rook_pos = (row, 8)
            path = [(row,6), (row,7)]
        else:
            rook_pos = (row, 1)
            path = [(row,4), (row,3), (row,2)]
        rook = self.piece_at(rook_pos)
        if not isinstance(rook, Rook) or rook.color != color or rook.moved:
            return False
        for r, c in path:
            if self.arr[r-1][c-1] != " ":
                return False
        enemy = "black" if color == "white" else "white"
        attacked = self.squares_attacked_by(enemy)
        check_squares = [(row,5), (row,6 if king_side else 4), (row,7 if king_side else 3)]
        for sq in check_squares:
            if sq in attacked:
                return False
        return True

    def perform_castle(self, color: str, king_side: bool):
        row = 1 if color == "white" else 8
        king = self.kings[color]
        if king_side:
            self.move_piece_obj(king, (row,7))
            rook = self.piece_at((row,8))
            self.move_piece_obj(rook, (row,6))
        else:
            self.move_piece_obj(king, (row,3))
            rook = self.piece_at((row,1))
            self.move_piece_obj(rook, (row,4))

    def legal_moves_for(self, p: Piece) -> List[Position]:
        raw = p.gen_moves(self)
        legal: List[Position] = []
        for dest in raw:
            snap = self._snapshot()
            self._apply_move_sim(p.pos(), dest)
            if not self.in_check(p.color):
                legal.append(dest)
            self._restore_snapshot(snap)
        return legal

    def get_all_legal_moves(self, color: str) -> List[Tuple[Position, Position]]:
        moves = []
        # Iterate over a copy of the dictionary to avoid "dictionary keys changed during iteration" error
        for pos, p in list(self.pieces.items()):
            if p.color == color:
                legal_dests = self.legal_moves_for(p)
                for dest in legal_dests:
                    moves.append((pos, dest))
        return moves

    def _snapshot(self):
        # Create a deep copy of all pieces to preserve their state and identity
        pieces_copy = {}
        for pos, pc in self.pieces.items():
            cls = pc.__class__
            np = cls(pc.row, pc.col, pc.color)
            np.moved = pc.moved
            pieces_copy[pos] = np
        
        # Create a new mapping for kings to the new piece objects
        kings_copy = {}
        for color, king in self.kings.items():
            king_pos = king.pos()
            kings_copy[color] = pieces_copy.get(king_pos)
            
        arr_copy = [row[:] for row in self.arr]
        
        # Deep copy the captured_pieces lists as well
        captured_pieces_copy = {k: [p.__class__(p.row, p.col, p.color) for p in v] for k, v in self.captured_pieces.items()}
        
        return (pieces_copy, kings_copy, arr_copy, self.to_move, self.en_passant_target, self.halfmove_clock, self.move_number, captured_pieces_copy)

    def _restore_snapshot(self, snap):
        pieces_copy, kings_copy, arr_copy, to_move, en_passant_target, halfmove_clock, move_number, captured_pieces = snap
        self.pieces = pieces_copy
        self.kings = kings_copy
        self.arr = self.board.return_array()
        for i in range(8):
            for j in range(8):
                self.arr[i][j] = arr_copy[i][j]
        self.to_move = to_move
        self.en_passant_target = en_passant_target
        self.halfmove_clock = halfmove_clock
        self.move_number = move_number
        self.captured_pieces = captured_pieces

    def _apply_move_sim(self, src: Position, dest: Position):
        p = self.piece_at(src)
        if p is None: return

        # Handle castling
        if isinstance(p, King) and abs(dest[1] - p.col) == 2:
            king_side = dest[1] > p.col
            self.perform_castle(p.color, king_side)
        
        # Handle en passant
        elif isinstance(p, Pawn) and self.en_passant_target == dest and self.arr[dest[0]-1][dest[1]-1] == " ":
            dir = 1 if p.color == "white" else -1
            capture_pos = (dest[0]-dir, dest[1])
            self.remove_at(capture_pos)
            self.move_piece_obj(p, dest)
        
        # Normal move
        else:
            self.move_piece_obj(p, dest)
    
    def _apply_move_permanent(self, src: Position, dest: Position, promotion_symbol: Optional[str]=None):
        p = self.piece_at(src)
        if p is None: return

        captured_piece = self.piece_at(dest)
        
        # Handle standard captures
        if captured_piece:
            self.captured_pieces[p.color].append(captured_piece)
        
        # Handle castling
        if isinstance(p, King) and abs(dest[1] - p.col) == 2:
            king_side = dest[1] > p.col
            self.perform_castle(p.color, king_side)
        
        # Handle en passant
        elif isinstance(p, Pawn) and self.en_passant_target == dest and self.arr[dest[0]-1][dest[1]-1] == " ":
            dir = 1 if p.color == "white" else -1
            captured_en_passant_pawn = self.piece_at((dest[0]-dir, dest[1]))
            if captured_en_passant_pawn: 
                self.captured_pieces[p.color].append(captured_en_passant_pawn)
                self.remove_at((dest[0]-dir, dest[1]))
            self.move_piece_obj(p, dest)
        
        # Normal move
        else:
            self.move_piece_obj(p, dest)
        
        # Handle promotion
        if isinstance(p, Pawn) and ((dest[0] == 8 and p.color == "white") or (dest[0] == 1 and p.color == "black")):
            self.remove_at(dest)
            self._promote_piece(p, dest, promotion_symbol)
            
        # Set en passant target if a pawn made a double-step move
        if isinstance(p, Pawn) and abs(dest[0] - src[0]) == 2:
            mid_row = (dest[0] + src[0]) // 2
            self.en_passant_target = (mid_row, dest[1])
        else:
            self.en_passant_target = None
            
    def make_move(self, src: Position, dest: Position, promotion_symbol: Optional[str]=None) -> bool:
        p = self.piece_at(src)
        if p is None or p.color != self.to_move:
            return False
            
        legal_moves = self.legal_moves_for(p)
        
        if dest not in legal_moves:
            return False
            
        is_pawn_or_capture = isinstance(p, Pawn) or self.piece_at(dest) is not None
        
        # Handle promotion
        if isinstance(p, Pawn) and ((dest[0] == 8 and p.color == "white") or (dest[0] == 1 and p.color == "black")):
            if not promotion_symbol:
                # If no promotion symbol is provided, don't make the move. The GUI will handle this.
                return False
            self._apply_move_permanent(src, dest, promotion_symbol)
        else:
            self._apply_move_permanent(src, dest)

        # Update game state
        if is_pawn_or_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        self.to_move = "black" if self.to_move == "white" else "white"
        if self.to_move == "white":
            self.move_number += 1
            
        return True

    def _promote_piece(self, pawn: Pawn, pos: Position, symbol: str):
        self.remove_at(pos)
        r, c = pos
        symbol = symbol.upper() if pawn.color == "white" else symbol.lower()
        if symbol.upper() == 'Q':
            newp = Queen(r, c, pawn.color)
        elif symbol.upper() == 'R':
            newp = Rook(r, c, pawn.color)
        elif symbol.upper() == 'B':
            newp = Bishop(r, c, pawn.color)
        else:
            newp = Knight(r, c, pawn.color)
        newp.moved = True
        self._place(newp)

    def has_any_legal_moves(self, color: str) -> bool:
        # Iterate over a copy of the dictionary to avoid "dictionary keys changed during iteration" error
        for pos, p in list(self.pieces.items()):
            if p.color != color:
                continue
            if self.legal_moves_for(p):
                return True
        return False

    def outcome(self) -> Optional[str]:
        if self.in_check(self.to_move):
            if not self.has_any_legal_moves(self.to_move):
                return f"Checkmate — {'White' if self.to_move=='black' else 'Black'} wins!"
            return None
        else:
            if not self.has_any_legal_moves(self.to_move):
                return "Stalemate — draw."
        return None

    def piece_value(self, piece: Piece) -> int:
        if isinstance(piece, Pawn): return 1
        if isinstance(piece, Knight) or isinstance(piece, Bishop): return 3
        if isinstance(piece, Rook): return 5
        if isinstance(piece, Queen): return 9
        return 0

    def evaluate_board(self, color):
        """A simple evaluation function for the AI to determine board state value."""
        score = 0
        for p in self.pieces.values():
            if p.color == color:
                score += self.piece_value(p)
            else:
                score -= self.piece_value(p)
        return score

    def ai_move(self):
        """Finds and makes the best move for the AI using a simple Minimax algorithm."""
        best_score = -float('inf')
        best_move = None
        
        legal_moves = self.get_all_legal_moves("black")
        random.shuffle(legal_moves)
        
        for src, dest in legal_moves:
            snapshot = self._snapshot()
            self._apply_move_permanent(src, dest)
            
            score = self.minimax(1, -float('inf'), float('inf'), False)
            
            self._restore_snapshot(snapshot)
            
            if score > best_score:
                best_score = score
                best_move = (src, dest)
                
        if best_move:
            self.make_move(best_move[0], best_move[1])

    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self.evaluate_board("black")

        if maximizing_player:
            max_eval = -float('inf')
            legal_moves = self.get_all_legal_moves("black")
            for src, dest in legal_moves:
                snapshot = self._snapshot()
                self._apply_move_permanent(src, dest)
                
                evaluation = self.minimax(depth - 1, alpha, beta, False)
                self._restore_snapshot(snapshot)
                
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            legal_moves = self.get_all_legal_moves("white")
            for src, dest in legal_moves:
                snapshot = self._snapshot()
                self._apply_move_permanent(src, dest)
                
                evaluation = self.minimax(depth - 1, alpha, beta, True)
                self._restore_snapshot(snapshot)
                
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    game = Game()
    gui = ChessGUI(game)
    gui.run()
