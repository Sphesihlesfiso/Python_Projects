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

    def __init__(self, row: int, col: int, representation: str,color:str):
        """
        Initializes a chess piece with its position and representation.

        :param row: The row position (1-indexed).
        :param col: The column position (1-indexed).
        :param representation: The visual representation of the piece.
        """
        self.row = row
        self.col = col
        self.color=color
        self.representation = representation if color=="white" else representation.lower()
        

    def get_positions_available(self,row,col)->list:
        """
        Placeholder method to be implemented in subclasses.

        :return: List of valid positions the piece can move to.
        """
        pass
    def return_representation(self)->str:
        """
        Returns the character representation of the chess piece.
  
        :return: str - The representation of the piece.
        """
        return self.representation
    
    def validate_move_and_move(self,row,col)->bool:# rename to appropiate name
        if array[row-1][col-1]==Chesspiece.return_representation(self):
            return True
        else:
            print("No Chesspiece at selected position!")

            return False

    def promote_piece(self):
        pass
    def capture_piece(self):
        pass
class Pawn(Chesspiece):
    """
    Represents a Pawn chess piece.
    """
    def __init__(self, row: int, col:int,color:str):
        """
        Initializes a Pawn piece.

        :param row: The row position.
        :param col: The column position.
        :param moved bool: To know its the first move or not
        """
        self.moved=False
        super().__init__(row, col, representation ="P",color=color)
    def get_positions_available(self, row, col):
        available = []

        direction = 1 if self.color == "white" else -1 # white moves up (row decreases), black moves down (row increases)
        if not self.moved:
            i, j = (1, 3) if self.color == "white" else (6, 8)

            # Initial 2-step move
            for step in range(i, j):
                next_row = row + step * direction
                if 1 <= next_row <= 8:
                    available.append((next_row, col))
                    array[next_row - 1][col - 1] = "z"
        else:
            next_row = row+direction
            if 1 <= next_row <= 8:
                available.append((next_row, col))
                array[next_row - 1][col -1]="z"
        print(available)
        return available
    def move_piece(self, row, col, next_row, next_col):
        if self.row >5 :
            color="black"
            exit()
        else:
            color=color
        print(self.representation)
        if array[row - 1][col - 1] == self.representation:
            available = self.get_positions_available(row, col)
            board_object.erase_x()
            print(self.color)
            if (next_row, next_col) in available:
                array[row-1 ][col-1] = " "
                array[next_row-1 ][next_col-1] = self.representation
                self.row = next_row  # Update the pawn's position
                self.col = next_col
                print(self.row,self.col)
                self.moved = True
            else:
                print("Invalid position! Please choose a valid position.")
        else:
            print(f"No piece at {row} {col}")


        

class Rook(Chesspiece):
    """
    Represents a Rook chess piece.

    The Rook moves vertically and horizontally without limitations.
    """

    def __init__(self, row: int, col: int,color):
        """
        Initializes a Rook piece.

        :param row: The row position.
        :param col: The column position.
        """
        super().__init__(row, col, representation="R",color=color)

    def get_positions_available(self,row,col):
        """
        Computes all valid positions the Rook can move to.

        :return: List of tuples representing valid positions (row, col).
        """
        # if super().validate_move_and_move(row,col):
        available_positions = []
        array = board_object.array
        # Moving horizontally
    # Moving horizontally
        for j in range(0, 8):
            print(row, j)
            if 0 <= row <= 8 and 0 <= j <= 8 and array[row - 1][j] == " ":
                array[row - 1][j] = "x"
                available_positions.append((row, j))
        # Moving vertically
        for row in range(0, 8):
            print(row,    col)
            if 0 <= row <= 8 and 0 <= col <= 8 and array[row][col-1] == " ":
                array[row][col-1 ] = "x"
                available_positions.append((row, col))
            else:
                print("yeah")

            


class Bishop(Chesspiece):
    """
    Represents a Bishop chess piece.

    The Bishop moves diagonally in any direction.
    """

    def __init__(self, row: int, col: int,color):
        """
        Initializes a Bishop piece.

        :param row: The row position.
        :param col: The column position.
        """
        self.color=color
        super().__init__(row, col, representation="B",color=color)

    def get_positions_available(self,row,col): 
        """
        Computes all valid diagonal moves for the Bishop.

        :return: List of tuples representing valid diagonal positions (row, col).
        """
        diagonals = []

        # Generating diagonal moves
        for i, j in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = row + i, col + j  # use temp vars to not overwrite input
            while 0 <= r <= 8 and 0 <= c <= 8:
                diagonals.append((r, c))
                r += i
                c += j

        # Mark valid moves
        for r, c in diagonals:
            if array[r-1][c-1] == " " and 0 <= r-1 <= 8 and 0 <= c-1 <= 8:
                array[r-1][c-1] = "x"
            else:
                pass


class Queen(Chesspiece):
    """
    Represents a Queen chess piece.

    The Queen moves like both a Rook and a Bishop.
    """

    def __init__(self, row: int, col: int,color):
        """
        Initializes a Queen piece.

        :param row: The row position.
        :param col: The column position.
        """
        
        super().__init__(row, col, representation="Q",color=color)
        self.diagonal_movement = Bishop(self.row, self.col,color=color)
        self.horizontal_vertical = Rook(self.row, self.col,color=color)

    def get_positions_available(self,row,col):
        """
        Computes all valid moves for the Queen (both diagonal and straight-line moves).

        :return: List of tuples representing valid positions.
        """
        # array = board_object.array
        # possible_moves=[self.diagonal_movement.diagonal_positions() + self.horizontal_vertical.get_positions_available()]
        
        
        self.diagonal_movement = self.diagonal_movement.get_positions_available(row,col)
        self.horizontal_vertical = self.horizontal_vertical.get_positions_available(row,col)
        
class Knight(Chesspiece):
    """
    Represents a Knight chess piece.

    The Knight moves in an 'L' shape: two squares in one direction, then one square perpendicular.
    """

    def __init__(self, row: int, col: int,color):
        """
        Initializes a Knight piece.

        :param row: The row position.
        :param col: The column position.
        """
        self.color=color
        super().__init__(row, col, representation="H",color=color)

    def get_positions_available(self,row,col):
        """
        Computes all valid moves for the Knight.

        :return: List of tuples representing valid positions (row, col).
        """
        array = board_object.array
        possible_moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]
        # Mark valid moves
        for row, col in possible_moves:
            if 1 <= row <= 8 and 1 <= col <= 8 and array[row - 1][col - 1] == " ":
                array[row - 1][col - 1] = "x"

        return possible_moves
class King(Chesspiece):
    def __init__(self, row, col,color):
           super().__init__(row, col, representation="K",color=color)

