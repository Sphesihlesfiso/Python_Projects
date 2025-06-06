
#This file contains the chess board object and all the methods assocciated with a chess board
class Board:
    """
    """
    def __init__(self)->str:
        self.array=[[" " for i in range(8)] for j in range(8)]
    def return_array(self)->list:
        return self.array
    def Put_piece(self,i,j,piece):
        
        self.array[i-1][j-1]=piece
    def Draw_board(self):
        letters=['a','b','c','d','e','f','g','h']
        for i in letters:
            print("  "+str(i),end="")
        print()
        for i in range(len(self.array)):
            print(" "+"+--"*8+"+")
            print(str(1+i)+"|",end=" ")
            for j in range(len(self.array)):
                if j!=7:
                    print(f"{self.array[i][j]}|",end=" ") 
                else:
                    print(f"{self.array[i][j]}|"+str(i+1),end=" ""\n") 
        print(" "+"+--"*8+"+")
        for i in letters:
            print("  "+str(i),end="")





