from Chessboard import Board
from pieces import Rook,Pawn,board_object,Quenn,Bishop
import sys

def create_pieces()->list:
    white_Rooks=[]
    white_Rook1=Rook(1,1)
    white_Rook2=Rook(1,8)
    white_Rooks.append(white_Rook1)
    white_Rooks.append(white_Rook2)
    return white_Rooks

def main(args):
    
    Rooks=create_pieces()
    pawns=[]
    for row in range(1,5):
        for col in range(1,5):
            pawn=Pawn(row,col)
            pawns.append(pawn)
   
    for pawn in Rooks:
        board_object.Put_piece(pawn.row,pawn.col,pawn.represantation)
       # pawn.get_postions_available()
    # for pawn in pawns:
    #     Chess_board.Put_piece(pawn.row,pawn.col,pawn.represantation)
   
    # b=Bishop(5,5)
    # board_object.Put_piece(b.row,b.col,b.represantation)
    # b.diagonal_positions()
    b=Quenn(5,5)
    board_object.Put_piece(b.row,b.col,b.represantation)
    b.diagonal_vertical_horizontal_positions()
    board_object.Draw_board()
if __name__=="__main__":
    main(sys.argv)