from Chessboard import Board
from pieces import Rook,Pawn,board_object,Queen,Bishop,Knight,King
import sys



def create_pieces() -> list:
    rooks = []
    bishops = []
    knights = []
    queens = []
    kings = []
    pawns = []

    # Rooks
    rooks.append(Rook(1, 1, "white"))
    rooks.append(Rook(1, 8, "white"))
    rooks.append(Rook(8, 1, "black"))
    rooks.append(Rook(8, 8, "black"))

    # Bishops
    bishops.append(Bishop(1, 3, "white"))
    bishops.append(Bishop(1, 6, "white"))
    bishops.append(Bishop(8, 3, "black"))
    bishops.append(Bishop(8, 6, "black"))

    # Knights
    knights.append(Knight(1, 2, "white"))
    knights.append(Knight(1, 7, "white"))
    knights.append(Knight(8, 2, "black"))
    knights.append(Knight(8, 7, "black"))

    # Queens
    queens.append(Queen(1, 5, "white"))
    queens.append(Queen(8, 5, "black"))

    # Kings
    kings.append(King(1, 4, "white"))
    kings.append(King(8, 4, "black"))

    # Pawns
    for i in range(8):
        pawns.append(Pawn(7, i + 1, "black"))  # white pawns
        pawns.append(Pawn(2, i + 1, "white"))  # black pawns

    return rooks, knights, bishops, queens, kings, pawns
def main(args):
    rooks, knights, bishops, queens, kings, pawns = create_pieces()
    # You can now handle each type separately, using their color attribute when needed.

    for rook in rooks:
        board_object.Put_piece(rook.row, rook.col, rook.representation)

# Place knights
    for knight in knights:
        board_object.Put_piece(knight.row, knight.col, knight.representation)

    # Place bishops
    for bishop in bishops:
        board_object.Put_piece(bishop.row, bishop.col, bishop.representation)

    # Place queens
    for queen in queens:
        board_object.Put_piece(queen.row, queen.col, queen.representation)

    # Place kings
    for king in kings:
        board_object.Put_piece(king.row, king.col, king.representation)

    # Place pawns
    for pawn in pawns:
        board_object.Put_piece(pawn.row, pawn.col, pawn.representation)
    pawn.get_positions_available(2,5)
    

    board_object.Draw_board()
if __name__=="__main__":
    main(sys.argv)
   