from Chessboard import Board
from pieces import Rook,Pawn,board_object,Queen,Bishop,Knight,King
import sys



def create_pieces()->list:
    white_Rooks=[]
    white_pawns=[]
    white_horses=[]
    white_pawns=[]
    white_Bishops=[]
    white_Rook1=Rook(1,1)
    white_Rook2=Rook(1,8)
    white_Bishop1=Bishop(1,3)
    white_Bishop2=Bishop(1,6)
    white_horse1=Knight(1,2)
    white_horse2=Knight(1,7)
    white_Queen=Queen(1,5)
    white_king=King(1,4)
    for i in range(8):
        white_pawn=Pawn(2,i)
        white_pawns.append(white_pawn)
    white_Bishops.append(white_Bishop1)
    white_Bishops.append(white_Bishop2)
    white_Rooks.append(white_Rook1)
    white_Rooks.append(white_Rook2)
    white_horses.append(white_horse1)
    white_horses.append(white_horse2)
    return white_Rooks,white_horses,white_Bishops,white_Queen,white_king,white_pawns
def get_user_input():
    pass
def main(args):
    white_Rooks,white_horses,white_Bishops,white_Queen,white_king,white_pawns=create_pieces()
    # Place rooks, knights, and bishops first
    for rook in white_Rooks:
        board_object.Put_piece(rook.row, rook.col, rook.representation)
    rook.get_positions_available(8,8)
    # for horse in white_horses:
    #     board_object.Put_piece(horse.row, horse.col, horse.representation)
    # horse.get_positions_available(1,2)
    # for bishop in white_Bishops:
    #     board_object.Put_piece(bishop.row, bishop.col, bishop.representation)

    # # Place queen and king (only one each)
    # board_object.Put_piece(white_Queen.row, white_Queen.col, white_Queen.representation)
    # board_object.Put_piece(white_king.row, white_king.col, white_king.representation)

    # # Place pawns last
    # for pawn in white_pawns:
    #     board_object.Put_piece(pawn.row, pawn.col, pawn.representation)
    #     board_object.Put_piece(-pawn.row+1, -pawn.col, pawn.representation)
    
    
    # # pawn.erase_x()
    # for i in white_Rooks:
    #     i.get_positions_available()

    board_object.Draw_board()
if __name__=="__main__":
    main(sys.argv)
   