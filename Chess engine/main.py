# Fully playable terminal chess using provided Board class
# Features: legal move validation, captures, check, checkmate, stalemate, castling, en passant, promotion
# Input format: e.g., "e2 e4" or with promotion "e7 e8=Q". Type "help" for commands.

from Chessboard import Board
from typing import List, Tuple, Dict, Optional

board = Board()
board.init_board()

# ------------------- Helpers -------------------
FILE_TO_COL = {c: i+1 for i, c in enumerate("abcdefgh")}
COL_TO_FILE = {v: k for k, v in FILE_TO_COL.items()}

Position = Tuple[int, int]  # (row, col) 1-indexed

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

# ------------------- Piece Classes -------------------
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
            # Forward two squares
            r2 = self.row + 2*dir
            if self.row == start_row and in_bounds(r2, c1) and arr[r2-1][c1-1] == " " and arr[r1-1][c1-1] == " ":
                moves.append((r2, c1))
        
        # Captures
        for dc in (-1, 1):
            r, c = self.row + dir, self.col + dc
            if in_bounds(r, c):
                if self.is_enemy(arr, r, c):
                    moves.append((r, c))
                # En passant
                if game.en_passant_target == (r, c) and arr[r-1][c-1] == " ":
                    moves.append((r, c))
        return moves

# ------------------- Game Engine -------------------
class Game:
    def __init__(self):
        self.board = Board()
        self.board.init_board()
        self.arr = self.board.return_array()
        self.to_move = "white"
        self.pieces: Dict[Position, Piece] = {}
        self.kings: Dict[str, King] = {}
        self.en_passant_target: Optional[Position] = None
        self.halfmove_clock = 0
        self.move_number = 1
        self._setup_startpos()

    def _place(self, p: Piece):
        self.pieces[p.pos()] = p
        r, c = p.pos()
        self.arr[r-1][c-1] = p.symbol
        if isinstance(p, King):
            self.kings[p.color] = p

    def _setup_startpos(self):
        self.pieces.clear()
        self.kings.clear()
        # White pieces
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
        # Black pieces
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
            self.arr[r-1][c-1] = " "

    def move_piece_obj(self, p: Piece, dest: Position):
        self.remove_at(p.pos())
        p.set_pos(*dest)
        if dest in self.pieces:
            self.remove_at(dest)
        self.pieces[dest] = p
        r, c = dest
        self.arr[r-1][c-1] = p.symbol
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
            else:  # Sliding pieces
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
        king = self.kings[color]
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
            if self._apply_move_sim(p.pos(), dest, promotion_symbol="Q" if isinstance(p, Pawn) and (dest[0] == 8 or dest[0] == 1) else None, simulation=True):
                if not self.in_check(p.color):
                    legal.append(dest)
            self._restore_snapshot(snap)
        return legal

    def _snapshot(self):
        pieces_copy = {}
        for pos, pc in self.pieces.items():
            cls = pc.__class__
            np = cls(pc.row, pc.col, pc.color)
            np.moved = pc.moved
            pieces_copy[pos] = np
        kings_copy = {k: (v.row, v.col, v.moved) for k, v in self.kings.items()}
        arr_copy = [row[:] for row in self.arr]
        return (pieces_copy, kings_copy, arr_copy, self.to_move, self.en_passant_target, self.halfmove_clock, self.move_number)

    def _restore_snapshot(self, snap):
        pieces_copy, kings_copy, arr_copy, to_move, en_passant_target, halfmove_clock, move_number = snap
        self.pieces = {}
        self.arr = self.board.return_array()
        for i in range(8):
            for j in range(8):
                self.arr[i][j] = arr_copy[i][j]
        self.kings = {}
        for pos, pc in pieces_copy.items():
            self.pieces[pos] = pc
            if isinstance(pc, King):
                self.kings[pc.color] = pc
        self.to_move = to_move
        self.en_passant_target = en_passant_target
        self.halfmove_clock = halfmove_clock
        self.move_number = move_number

    def _apply_move_sim(self, src: Position, dest: Position, promotion_symbol: Optional[str], simulation: bool=False) -> bool:
        p = self.piece_at(src)
        if p is None:
            return False
        if isinstance(p, King) and not p.moved and (dest == (p.row, p.col+2) or dest == (p.row, p.col-2)):
            king_side = dest[1] > p.col
            if self.can_castle(p.color, king_side):
                self.perform_castle(p.color, king_side)
                return True
            return False
        if isinstance(p, Pawn) and self.en_passant_target == dest and self.arr[dest[0]-1][dest[1]-1] == " ":
            dir = 1 if p.color == "white" else -1
            capture_pos = (dest[0]-dir, dest[1])
            self.remove_at(capture_pos)
        self.move_piece_obj(p, dest)
        if isinstance(p, Pawn) and abs(dest[0] - src[0]) == 2:
            mid_row = (dest[0] + src[0]) // 2
            self.en_passant_target = (mid_row, dest[1])
        else:
            self.en_passant_target = None
        if isinstance(p, Pawn) and ((dest[0] == 8 and p.color == "white") or (dest[0] == 1 and p.color == "black")):
            if not simulation and not promotion_symbol:
                raise ValueError("Promotion piece required (e.g., e7 e8=Q)")
            promo = promotion_symbol or "Q"
            self._promote_piece(p, promo)
        return True

    def make_move(self, src: Position, dest: Position, promotion_symbol: Optional[str]=None) -> bool:
        p = self.piece_at(src)
        if p is None or p.color != self.to_move:
            print("No piece of yours on the source square.")
            return False
        raw = p.gen_moves(self)
        legal = self.legal_moves_for(p)
        print(f"DEBUG: Raw moves for {p.symbol} at {pos_to_algebraic(src)}: {' '.join(pos_to_algebraic(m) for m in raw)}")
        print(f"DEBUG: Legal moves for {p.symbol} at {pos_to_algebraic(src)}: {' '.join(pos_to_algebraic(m) for m in legal)}")
        if dest not in legal:
            print(f"Illegal move. Legal moves for {p.symbol} at {pos_to_algebraic(src)}: {' '.join(pos_to_algebraic(m) for m in legal)}")
            return False
        try:
            self._apply_move_sim(src, dest, promotion_symbol, simulation=False)
        except ValueError as e:
            print(e)
            return False
        if isinstance(p, Pawn) or self.piece_at(dest) is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        self.to_move = "black" if self.to_move == "white" else "white"
        if self.to_move == "white":
            self.move_number += 1
        return True

    def _promote_piece(self, pawn: Pawn, symbol: str):
        r, c = pawn.pos()
        self.remove_at((r,c))
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

    def print_board(self):
        self.board.erase_x()
        self.board.Draw_board()
        status = f"Turn {self.move_number} — To move: {self.to_move.capitalize()}"
        if self.in_check(self.to_move):
            status += " (in check)"
        print(status + "\n")

    def print_legal_moves(self, square_alg: str):
        try:
            pos = algebraic_to_pos(square_alg)
        except Exception as e:
            print(str(e))
            return
        p = self.piece_at(pos)
        if not p:
            print("No piece on that square.")
            return
        if p.color != self.to_move:
            print("That’s not your piece this turn.")
            return
        moves = self.legal_moves_for(p)
        if not moves:
            print("No legal moves for that piece.")
        else:
            print(f"Legal moves for {p.symbol} at {square_alg}: ", " ".join(sorted(pos_to_algebraic(m) for m in moves)))

# ------------------- Game Loop -------------------
HELP_TEXT = (
    "Commands:\n"
    "  move:          e2 e4\n"
    "  move+promo:    e7 e8=Q  (promotion to Q/R/B/N)\n"
    "  moves from:    moves e2  (show legal moves for your piece)\n"
    "  board:         board\n"
    "  resign:        resign\n"
    "  help:          help\n"
    "  quit:          quit\n"
)

def parse_move(s: str) -> Tuple[Position, Position, Optional[str]]:
    parts = s.strip().split()
    if len(parts) != 2:
        raise ValueError("Enter moves like: e2 e4  or  e7 e8=Q")
    src_alg, dst_alg = parts
    promo = None
    if '=' in dst_alg:
        dst_alg, promo = dst_alg.split('=')
        promo = promo.upper()
        if promo not in {"Q","R","B","N"}:
            raise ValueError("Promotion piece must be Q, R, B, or N")
    try:
        src = algebraic_to_pos(src_alg)
        dst = algebraic_to_pos(dst_alg)
    except ValueError as e:
        raise ValueError(str(e))
    return src, dst, promo

def main():
    game = Game()
    print("Welcome to Terminal Chess!\n")
    print(HELP_TEXT)
    game.print_board()

    while True:
        outcome = game.outcome()
        if outcome:
            print(outcome)
            break
        cmd = input(f"{game.to_move.capitalize()} to move > ").strip().lower()
        if not cmd:
            continue
        if cmd in ("quit","exit"):
            print("Goodbye!")
            break
        if cmd == "help":
            print(HELP_TEXT)
            continue
        if cmd == "board":
            game.print_board()
            continue
        if cmd.startswith("moves "):
            try:
                sq = cmd.split(maxsplit=1)[1]
                game.print_legal_moves(sq)
            except IndexError:
                print("Please specify a square (e.g., moves e2)")
            continue
        if cmd == "resign":
            winner = "Black" if game.to_move == "white" else "White"
            print(f"{winner} wins by resignation.")
            break
        try:
            src, dst, promo = parse_move(cmd)
        except ValueError as e:
            print(e)
            continue
        if game.make_move(src, dst, promo):
            game.print_board()
        else:
            p = game.piece_at(src)
            if p and p.color == game.to_move:
                legals = " ".join(sorted(pos_to_algebraic(m) for m in game.legal_moves_for(p)))
                if legals:
                    print("Legal moves:", legals)

if __name__ == "__main__":
    main()