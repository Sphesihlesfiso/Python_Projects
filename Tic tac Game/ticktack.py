"""
This is a tick tack game played by two players .
The one who can get their 3 makers X or O horizontaly verticaly or diagonally wins!
The game takes in one argument in the terminal to decide whether it will be played in the terminal or in the Graphical user interface(Gui).
"""
import sys
import pygame


def draw_game(board: list, screen, font):
    screen.fill((255, 255, 255))  
    width, height = screen.get_size()
    rows = len(board)
    cols = len(board[0])
    cell_width = width // cols
    cell_height = height // rows

    
    for i in range(1, rows):
        pygame.draw.line(screen, (0, 0, 0), (0, i * cell_height), (width, i * cell_height), 2)
    for j in range(1, cols):
        pygame.draw.line(screen, (0, 0, 0), (j * cell_width, 0), (j * cell_width, height), 2)

    # Draw pieces
    for row in range(rows):
        for col in range(cols):
            piece = board[row][col]
            if piece != ' ':
                text = font.render(piece, True, (0, 0, 0))
                text_rect = text.get_rect(center=(col * cell_width + cell_width // 2, row * cell_height + cell_height // 2))
                screen.blit(text, text_rect)

    pygame.display.flip()

def print_board(board:list,player:list)->str:
    """
    This function takes in an array where our game pieces will be stored while playing,
    and the player that is playing 
    It will print out the board in a nice format.
    """
    for row in board:
        print("  +---+---+---+")
        print("  |", end="")
        for cell in row:
            print(f" {cell} |", end="")  
        print() 
    print("  +---+---+---+")
def check_if_not_free(board:list,row,col)->bool:
    """
    This function will take the board as it argument.
    This function checks if the space a player is trying to put their piece in is free or not and gives an error
    message if the space is not free.
    """
    if board[row][col]!=" ":
        print(f"{row,col} is not free ,try onother postion!")
        return True if True else False

def check_for_win(board:list,piece:str,Player)->None:
    """
    Takes in the board as an argument 
    The function will check a player has put 3 of their pieces diagonally ,horizonantal or  vertically.
    """
    if Player=="Player_2" :
        piece="O"
    else:
        piece="X"
  
    for row in board:
        if row[0] == piece and row[1] == piece and row[2] == piece:
            print(f"{Player} Wins!")
            return True

    for col in range(3):  
        if board[0][col] == piece and board[1][col] == piece and board[2][col] == piece:
            print(f"{Player} Wins!")
            exit()
    if board[1][1]==piece  and board[2][0]==piece  and board[0][2]==piece or board[0][0] ==piece and board[1][1] ==piece and board[2][2]==piece :
        print(f"{Player} Wins!")
        
    else:
        return False

def check_for_draw(board):
    for row in board:
        if " " in row: 
            return False
    print("It's a draw!")
    exit()
def take_input_and_validate(Playing)->tuple:
    """
    function to take input from the user and validate it and return.
    It it can be a string or an int
    """
    while True :
        row_col=input(str(Playing)+" place your piece at any row and column eg (1 2) :").split()
        if len(row_col) ==2 and row_col[0].isdigit() and  row_col[1].isdigit() and 0<int(row_col[0])<=3 and 0< int(row_col[1])<=3:
            row,col=int(row_col[0])-1,int(row_col[1])-1
            return row,col
        print("Please enter a valid position on the board. Rows and columns must be numbers between 1 and 3.")
def place_on_board(board:list,piece:str,player:str,row,col:str)->None:
    "funtion will taken in the board the piece and palyer and places pieces on the board"
    if not(check_if_not_free(board,row,col)):
        board[row][col]=piece
def main(args: str) -> str:
    gui = sys.argv[1]
    board = [[" " for _ in range(3)] for _ in range(3)]
    playing = "Player_1"

    if gui in ("0", "1"):
        if gui == "1":
            
            pygame.init()
            width, height = 600, 600
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Sphe's Tic Tac Toe Game")
            font = pygame.font.SysFont("A", 72)

        while True:
            if gui == "1":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                draw_game(board, screen, font)
            else:
                print_board(board, playing)

            row, col = take_input_and_validate(playing)
            piece = "X" if playing == "Player_1" else "O"
            place_on_board(board, piece, playing, row, col)

            if check_for_win(board, piece, playing):
                if gui == "1":
                    draw_game(board, screen, font)
                    pygame.time.wait(2000)
                    pygame.quit()
                else:
                    print_board(board, playing)
                print(f"{playing} Wins!")
                exit()

            if check_for_draw(board):
                if gui == "1":
                    draw_game(board, screen, font)
                    pygame.time.wait(2000)
                    pygame.quit()
                print("It's a draw!")
                exit()

            playing = "Player_2" if playing == "Player_1" else "Player_1"

    else:
        print("The GUI indicator must be zero or one!")
if __name__=="__main__":
    main(sys.argv)
    
