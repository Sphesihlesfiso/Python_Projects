from Chessboard import Board
board_object = Board()
array = board_object.array


class Chesspiece:
    """
    This is the superclass for all chess pieces.

    Attributes:
        row (int): The row position of the chess piece (1-indexed).
        col (int): The column position of the chess piece (1-indexed).
        representation (str): The character representing the piece on the board.
        color (str): The color of the piece ('white' or 'black').
    """

    def __init__(self, row: int, col: int, representation: str, color: str):
        """
        Initializes a chess piece with its position and representation.

        :param row: The row position (1-indexed).
        :param col: The column position (1-indexed).
        :param representation: The visual representation of the piece.
        :param color: The color of the piece ('white' or 'black').
        """
        self.row = row
        self.col = col
        self.color = color
        self.representation = representation if color == "white" else representation.lower()
        

    def get_positions_available(self, row, col) -> list:
        """
        Placeholder method to be implemented in subclasses.

        :return: List of valid positions the piece can move to.
        """
        pass
    
    def return_representation(self) -> str:
        """
        Returns the character representation of the chess piece.
  
        :return: str - The representation of the piece.
        """
        return self.representation
    
    def validate_move_and_move(self, row, col) -> bool:
        """
        Validates if there's a piece at the specified position.
        
        :param row: Row to check
        :param col: Column to check
        :return: True if piece exists at position, False otherwise
        """
        if array[row-1][col-1] == self.return_representation():
            return True
        else:
            print("No Chesspiece at selected position!")
            return False

    def move_piece(self, row, col, next_row, next_col):
        """
        Generic move method for all chess pieces.
        
        :param row: Current row
        :param col: Current column
        :param next_row: Target row
        :param next_col: Target column
        """
        # First, clear any existing 'x' markers
        board_object.erase_x()
        
        # Check if there's the correct piece at the specified position
        if array[row - 1][col - 1] == self.representation:
            # Get available positions (this will mark them with 'x')
            available = self.get_positions_available(row, col)
            print(f"Available positions for {self.__class__.__name__} at ({row},{col}): {available}")
            
            if (next_row, next_col) in available:
                # Make the move
                array[row - 1][col - 1] = " "
                array[next_row - 1][next_col - 1] = self.representation
                self.row = next_row
                self.col = next_col
                print(f"{self.__class__.__name__} moved to ({self.row}, {self.col})")
                
                # Mark as moved for pawns
                if hasattr(self, 'moved'):
                    self.moved = True
            else:
                print(f"Invalid position! Available moves: {available}")
        else:
            print(f"No {self.__class__.__name__} at ({row}, {col}). Found: '{array[row - 1][col - 1]}' Expected: '{self.representation}'")
    
    def promote_piece(self):
        """Placeholder for piece promotion logic."""
        pass
    
    def capture_piece(self):
        """Placeholder for piece capture logic."""
        pass


class Pawn(Chesspiece):
    """
    Represents a Pawn chess piece.
    """
    
    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Pawn piece.

        :param row: The row position.
        :param col: The column position.
        :param color: The color of the piece.
        """
        self.moved = False
        super().__init__(row, col, representation="P", color=color)
    
    def get_positions_available(self, row, col) -> list:
        """
        Get available positions for the pawn.
        
        :param row: Current row position
        :param col: Current column position
        :return: List of available positions
        """
        available = []
        direction = -1 if self.color == "white" else 1  # white moves up (row decreases), black moves down
        
        # Forward movement
        next_row = row + direction
        if 1 <= next_row <= 8 and array[next_row - 1][col - 1] == " ":
            available.append((next_row, col))
            array[next_row - 1][col - 1] = "x"
            
            # If pawn hasn't moved and first square is free, check second square
            if not self.moved:
                next_row2 = row + 2 * direction
                if 1 <= next_row2 <= 8 and array[next_row2 - 1][col - 1] == " ":
                    available.append((next_row2, col))
                    array[next_row2 - 1][col - 1] = "x"
        
        # Diagonal capture moves (if there are enemy pieces)
        for dc in [-1, 1]:  # left and right diagonals
            capture_row = row + direction
            capture_col = col + dc
            if (1 <= capture_row <= 8 and 1 <= capture_col <= 8 and 
                array[capture_row - 1][capture_col - 1] != " " and
                array[capture_row - 1][capture_col - 1] != "x"):
                # Check if it's an enemy piece (different case indicates different color)
                piece_at_target = array[capture_row - 1][capture_col - 1]
                if ((self.color == "white" and piece_at_target.islower()) or 
                    (self.color == "black" and piece_at_target.isupper())):
                    available.append((capture_row, capture_col))
                    array[capture_row - 1][capture_col - 1] = "x"
        
        return available
    
    def move_piece(self, row, col, next_row, next_col):
        """
        Move the pawn to a new position.
        
        :param row: Current row
        :param col: Current column
        :param next_row: Target row
        :param next_col: Target column
        """
        # First, clear any existing 'x' markers
        board_object.erase_x()
        
        # Check if there's a pawn at the specified position
        if array[row - 1][col - 1] == self.representation:
            # Get available positions (this will mark them with 'x')
            available = self.get_positions_available(row, col)
            print(f"Available positions for pawn at ({row},{col}): {available}")
            
            if (next_row, next_col) in available:
                # Make the move
                array[row - 1][col - 1] = " "
                array[next_row - 1][next_col - 1] = self.representation
                self.row = next_row
                self.col = next_col
                self.moved = True
                print(f"Pawn moved to ({self.row}, {self.col})")
            else:
                print(f"Invalid position! Available moves: {available}")
        else:
            print(f"No pawn at ({row}, {col}). Found: '{array[row - 1][col - 1]}' Expected: '{self.representation}'")


class Rook(Chesspiece):
    """
    Represents a Rook chess piece.

    The Rook moves vertically and horizontally without limitations.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Rook piece.

        :param row: The row position.
        :param col: The column position.
        :param color: The color of the piece.
        """
        super().__init__(row, col, representation="R", color=color)

    def get_positions_available(self, row, col) -> list:
        """
        Computes all valid positions the Rook can move to.

        :param row: Current row position
        :param col: Current column position
        :return: List of tuples representing valid positions (row, col).
        """
        available_positions = []
        
        # Moving horizontally - right direction
        for j in range(col + 1, 9):
            if array[row - 1][j - 1] == " ":
                array[row - 1][j - 1] = "x"
                available_positions.append((row, j))
            else:
                # Check if it's an enemy piece we can capture
                piece_at_target = array[row - 1][j - 1]
                if ((self.color == "white" and piece_at_target.islower()) or 
                    (self.color == "black" and piece_at_target.isupper())):
                    available_positions.append((row, j))
                    array[row - 1][j - 1] = "x"
                break  # Stop after hitting any piece
        
        # Moving horizontally - left direction
        for j in range(col - 1, 0, -1):
            if array[row - 1][j - 1] == " ":
                array[row - 1][j - 1] = "x"
                available_positions.append((row, j))
            else:
                # Check if it's an enemy piece we can capture
                piece_at_target = array[row - 1][j - 1]
                if ((self.color == "white" and piece_at_target.islower()) or 
                    (self.color == "black" and piece_at_target.isupper())):
                    available_positions.append((row, j))
                    array[row - 1][j - 1] = "x"
                break  # Stop after hitting any piece
        
        # Moving vertically - down direction
        for i in range(row + 1, 9):
            if array[i - 1][col - 1] == " ":
                array[i - 1][col - 1] = "x"
                available_positions.append((i, col))
            else:
                # Check if it's an enemy piece we can capture
                piece_at_target = array[i - 1][col - 1]
                if ((self.color == "white" and piece_at_target.islower()) or 
                    (self.color == "black" and piece_at_target.isupper())):
                    available_positions.append((i, col))
                    array[i - 1][col - 1] = "x"
                break  # Stop after hitting any piece
        
        # Moving vertically - up direction
        for i in range(row - 1, 0, -1):
            if array[i - 1][col - 1] == " ":
                array[i - 1][col - 1] = "x"
                available_positions.append((i, col))
            else:
                # Check if it's an enemy piece we can capture
                piece_at_target = array[i - 1][col - 1]
                if ((self.color == "white" and piece_at_target.islower()) or 
                    (self.color == "black" and piece_at_target.isupper())):
                    available_positions.append((i, col))
                    array[i - 1][col - 1] = "x"
                break  # Stop after hitting any piece
        
        return available_positions


class Bishop(Chesspiece):
    """
    Represents a Bishop chess piece.

    The Bishop moves diagonally in any direction.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Bishop piece.

        :param row: The row position.
        :param col: The column position.
        :param color: The color of the piece.
        """
        super().__init__(row, col, representation="B", color=color)

    def get_positions_available(self, row, col) -> list: 
        """
        Computes all valid diagonal moves for the Bishop.

        :param row: Current row position
        :param col: Current column position
        :return: List of tuples representing valid diagonal positions (row, col).
        """
        available_positions = []

        # Four diagonal directions: up-left, up-right, down-left, down-right
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 1 <= r <= 8 and 1 <= c <= 8:
                if array[r - 1][c - 1] == " ":
                    array[r - 1][c - 1] = "x"
                    available_positions.append((r, c))
                    r += dr
                    c += dc
                else:
                    # Check if it's an enemy piece we can capture
                    piece_at_target = array[r - 1][c - 1]
                    if ((self.color == "white" and piece_at_target.islower()) or 
                        (self.color == "black" and piece_at_target.isupper())):
                        available_positions.append((r, c))
                        array[r - 1][c - 1] = "x"
                    break  # Stop after hitting any piece
        
        return available_positions


class Queen(Chesspiece):
    """
    Represents a Queen chess piece.

    The Queen moves like both a Rook and a Bishop.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Queen piece.

        :param row: The row position.
        :param col: The column position.
        :param color: The color of the piece.
        """
        super().__init__(row, col, representation="Q", color=color)

    def get_positions_available(self, row, col) -> list:
        """
        Computes all valid moves for the Queen (both diagonal and straight-line moves).

        :param row: Current row position
        :param col: Current column position
        :return: List of tuples representing valid positions.
        """
        available_positions = []
        
        # Combine rook and bishop movements
        # Horizontal and vertical movements (like a rook)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 1 <= r <= 8 and 1 <= c <= 8:
                if array[r - 1][c - 1] == " ":
                    array[r - 1][c - 1] = "x"
                    available_positions.append((r, c))
                    r += dr
                    c += dc
                else:
                    break  # Stop if blocked by another piece
        
        return available_positions


class Knight(Chesspiece):
    """
    Represents a Knight chess piece.

    The Knight moves in an 'L' shape: two squares in one direction, then one square perpendicular.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a Knight piece.

        :param row: The row position.
        :param col: The column position.
        :param color: The color of the piece.
        """
        super().__init__(row, col, representation="H", color=color)

    def get_positions_available(self, row, col) -> list:
        """
        Computes all valid moves for the Knight.

        :param row: Current row position
        :param col: Current column position
        :return: List of tuples representing valid positions (row, col).
        """
        available_positions = []
        possible_moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]
        
        # Check each possible knight move
        for r, c in possible_moves:
            if 1 <= r <= 8 and 1 <= c <= 8:
                piece_at_target = array[r - 1][c - 1]
                if piece_at_target == " ":
                    # Empty square
                    array[r - 1][c - 1] = "x"
                    available_positions.append((r, c))
                elif ((self.color == "white" and piece_at_target.islower()) or 
                      (self.color == "black" and piece_at_target.isupper())):
                    # Enemy piece can be captured
                    array[r - 1][c - 1] = "x"
                    available_positions.append((r, c))

        return available_positions


class King(Chesspiece):
    """
    Represents a King chess piece.

    The King moves one square in any direction.
    """

    def __init__(self, row: int, col: int, color: str):
        """
        Initializes a King piece.

        :param row: The row position.
        :param col: The column position.
        :param color: The color of the piece.
        """
        super().__init__(row, col, representation="K", color=color)

    def get_positions_available(self, row, col) -> list:
        """
        Computes all valid moves for the King (one square in any direction).

        :param row: Current row position
        :param col: Current column position
        :return: List of tuples representing valid positions (row, col).
        """
        available_positions = []
        possible_moves = [
            (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
            (row, col - 1),                      (row, col + 1),
            (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)
        ]
        
        # Check each possible king move
        for r, c in possible_moves:
            if 1 <= r <= 8 and 1 <= c <= 8:
                piece_at_target = array[r - 1][c - 1]
                if piece_at_target == " ":
                    # Empty square
                    array[r - 1][c - 1] = "x"
                    available_positions.append((r, c))
                elif ((self.color == "white" and piece_at_target.islower()) or 
                      (self.color == "black" and piece_at_target.isupper())):
                    # Enemy piece can be captured
                    array[r - 1][c - 1] = "x"
                    available_positions.append((r, c))

        return available_positions