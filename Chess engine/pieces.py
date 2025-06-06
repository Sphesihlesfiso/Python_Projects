from Chessboard import Board
import timer

board_object = Board()
array = board_object.array
class Chesspiece:
    """
    This is the superclass for all chess pieces.

    Attributes:
        row (int): The row position of the chess piece (1-indexed).
        col (int): The column position of the chess piece (1-indexed).
        representation (str): The character representing the piece on the board.
    """

    def __init__(self, row: int, col: int, representation: str):
        """
        Initializes a chess piece with its position and representation.

        :param row: The row position (1-indexed).
        :param col: The column position (1-indexed).
        :param representation: The visual representation of the piece.
        """
        self.row = row
        self.col = col
        self.representation = representation

    def get_positions_available(self):
        """
        Placeholder method to be implemented in subclasses.

        :return: List of valid positions the piece can move to.
        """
        pass

    def return_representation(self):
        """
        Returns the character representation of the chess piece.

        :return: str - The representation of the piece.
        """
        return self.representation
    def erase_x(self):
        for i in range(0,8):
            for j in range(0,8):
                if array[i][j]=="x":
                    array[i][j]="x"
    def validate_move_and_move(self,postions)->bool:
        pass
    def promote_piece(self):
        pass
    def capture_piece(self):
        pass
class Pawn(Chesspiece):
    """
    Represents a Pawn chess piece.
    """
    def __init__(self, row: int, col: int):
        """
        Initializes a Pawn piece.

        :param row: The row position.
        :param col: The column position.
        :param moved bool: To know its the first move or not
        """
        self.moved=False
        super().__init__(row, col, representation="P")
    def get_positions_available(self,row,col):
        move_count=0
        available=[]
        if self.moved==False:
            print("Nee Slava Russisa")
            for i in range(3,5):
                available.append((i,col))
                # array[i-1][col-1]="x"
                print(available)
            return available
        else:
            if 1 <= row + 1<= 8 and 1 <= col <= 8:
               available.append((row + 1, col))
               print("Slava Russisa")
            return available

    def move_piece(self,row,col,next_row,next_col):
        if array[row-1][col-1]==Pawn.return_representation(self):
            array[row-1][col-1]=" "
            available=Pawn.get_positions_available(self,row,col)
           
            if (next_row,next_col) in available:
                print(next_row,next_col)

                array[next_row-1][next_col-1]=Pawn.return_representation(self)
                self.moved=True
            else:
                print(available)
        else:
            print(f"No piece at {row} {col}")
        

class Rook(Chesspiece):
    """
    Represents a Rook chess piece.

    The Rook moves vertically and horizontally without limitations.
    """

    def __init__(self, row: int, col: int):
        """
        Initializes a Rook piece.

        :param row: The row position.
        :param col: The column position.
        """
        super().__init__(row, col, representation="R")

    def get_positions_available(self):
        """
        Computes all valid positions the Rook can move to.

        :return: List of tuples representing valid positions (row, col).
        """
        available_positions = []
        array = board_object.array

        # Moving horizontally
        for col in range(0, 8):
            if array[self.row - 1][col] == " ":
                array[self.row - 1][col] = "x"
                available_positions.append((self.row, col))

        # Moving vertically
        for row in range(0, 8):
            if  1 <= row <= 8 and 1 <= self.col <= 8 and array[row][self.col - 1] == " ":
                print(row,self.col-1)
                array[row][self.col - 1] = "x"
                available_positions.append((row, self.col - 1))
            else:
                break
        return available_positions


class Bishop(Chesspiece):
    """
    Represents a Bishop chess piece.

    The Bishop moves diagonally in any direction.
    """

    def __init__(self, row: int, col: int):
        """
        Initializes a Bishop piece.

        :param row: The row position.
        :param col: The column position.
        """
        super().__init__(row, col, representation="B")

    def diagonal_positions(self):
        """
        Computes all valid diagonal moves for the Bishop.

        :return: List of tuples representing valid diagonal positions (row, col).
        """
        diagonals = []

        # Generating diagonal moves
        for i, j in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = self.row + i, self.col + j
            while 1 <= r <= 8 and 1 <= c <= 8:
                diagonals.append((r, c))
                r += i
                c += j

        array = board_object.array

        # Mark valid moves

        for r, c in diagonals:
            if  1 <= r <= 8 and 1 <= c <= 8 and array[r - 1][c - 1] == " ":
                array[r - 1][c - 1] = "x"


class Queen(Chesspiece):
    """
    Represents a Queen chess piece.

    The Queen moves like both a Rook and a Bishop.
    """

    def __init__(self, row: int, col: int):
        """
        Initializes a Queen piece.

        :param row: The row position.
        :param col: The column position.
        """
        super().__init__(row, col, representation="Q")
        self.diagonal_movement = Bishop(self.row, self.col)
        self.horizontal_vertical = Rook(self.row, self.col)

    def diagonal_vertical_horizontal_positions(self):
        """
        Computes all valid moves for the Queen (both diagonal and straight-line moves).

        :return: List of tuples representing valid positions.
        """
        # array = board_object.array
        # possible_moves=[self.diagonal_movement.diagonal_positions() + self.horizontal_vertical.get_positions_available()]
        
        
        self.diagonal_movement = self.diagonal_movement.diagonal_positions()
        self.horizontal_vertical = self.horizontal_vertical.get_positions_available()
        
class Knight(Chesspiece):
    """
    Represents a Knight chess piece.

    The Knight moves in an 'L' shape: two squares in one direction, then one square perpendicular.
    """

    def __init__(self, row: int, col: int):
        """
        Initializes a Knight piece.

        :param row: The row position.
        :param col: The column position.
        """
        super().__init__(row, col, representation="H")

    def get_positions_available(self):
        """
        Computes all valid moves for the Knight.

        :return: List of tuples representing valid positions (row, col).
        """
        array = board_object.array
        possible_moves = [
            (self.row + 2, self.col + 1), (self.row + 2, self.col - 1),
            (self.row - 2, self.col + 1), (self.row - 2, self.col - 1),
            (self.row + 1, self.col + 2), (self.row + 1, self.col - 2),
            (self.row - 1, self.col + 2), (self.row - 1, self.col - 2)
        ]

        # Mark valid moves
        for r, c in possible_moves:
            if 1 <= r <= 8 and 1 <= c <= 8 and array[r - 1][c - 1] == " ":
                array[r - 1][c - 1] = "x"

        return possible_moves
class King(Chesspiece):
    def __init__(self, row, col):
        super().__init__(row, col, representation="K")
