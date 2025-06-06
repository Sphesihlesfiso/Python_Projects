from Chessboard import Board
board_object=Board()
class Chesspiece:
    def __init__(self,row:int,col:int,represantation):
        self.row=row
        self.col=col
        self.represantation=represantation 
    def get_postions_available(self):
        pass
    def return_represantaion(self):
        return self.represantation
class Pawn(Chesspiece):
    def __init__(self,row,col):
        super().__init__(row,col,represantation="P")
class Rook(Chesspiece):
    def __init__(self,row,col):
        super().__init__(row,col,represantation="R")
    def get_postions_available(self):
        available_positions=[]
        for col in range(0,8): 
            array=board_object.array
            if array[self.row-1][col]==" " :
                array[self.row-1][col]="x"
                available_positions.append((self.row,col))
        for row in range(0,8):
            if array[row][self.col-1]==" " :
                array[row][self.col-1]="x"
                available_positions.append((row,self.col-1))
                # board_object.Put_piece(1,3,"x")
        return available_positions
class Bishop(Chesspiece):
    def __init__(self, row, col):
        super().__init__(row, col, represantation="B")
    def diagonal_positions(self):
        diagonals = []

        # Top-left diagonal
        i, j = self.row - 1, self.col - 1
        while i >= 1 and j >= 1:
            diagonals.append((i, j))
            i -= 1
            j -= 1

        # Top-right diagonal
        i, j = self.row - 1, self.col + 1
        while i >= 1 and j <= 8:
            diagonals.append((i, j))
            i -= 1
            j += 1

        # Bottom-left diagonal
        i, j = self.row + 1, self.col - 1
        while i <= 8 and j >= 1:
            diagonals.append((i, j))
            i += 1
            j -= 1

        # Bottom-right diagonal
        i, j = self.row + 1, self.col + 1
        while i <= 8 and j <= 8:
            diagonals.append((i, j))
            i += 1
            j += 1

        array = board_object.array  # Assuming array is 0-indexed: array[0][0] is (1,1)
        
        for r, c in diagonals:
            if array[r - 1][c - 1] == " ":
                array[r - 1][c - 1] = "x"
class Quenn(Chesspiece):
    def __init__(self, row, col):
        super().__init__(row, col,represantation="Q")
        self.diagonal_movement=Bishop(self.row,self.col)
        self.Horizontal_vertical=Rook(self.row,self.col)
    def diagonal_vertical_horizontal_positions(self):
        self.diagonal_movement=self.diagonal_movement.diagonal_positions()
        self.Horizontal_vertical=self.Horizontal_vertical.get_postions_available()
class Knight(Chesspiece):
    def __init__(self, row, col):
        super().__init__(row, col, represantation="H")
    






