from random import shuffle
"""
CMPUT 175 - Assignment 2 Template
"""

"""
Hints:
    - self.gameBoard represents the game board
    - self.playerColour represents the colour of the human player
    - self.computerColour represents the colour of the computer
    - the colour arguments are eiter self.WHITE or self.BLACK, which are defined below
"""
def main():
    
    s = Reversi()
    s.newGame()
    print('Starting new game!')
    print('Black goes first, then white')
    #get player colour and handle otherwise
    cvalid = False
    while not cvalid:
        colour = input("Enter 'b' to choose to play black, 'w' to choose white: ")
        if colour == 'w' or colour == 'b':
            s.setPlayerColour(colour)
            cvalid = True
    #get difficulty and handle otherwise
    diffvalid = False
    while not diffvalid:
        diff = input("Enter '1' to choose easy computer opponent, '2' for hard computer opponent: ")
        if diff == '1' or diff == '2':
            diffvalid = True    
    print(diff)
    s.displayBoard()
    turn = 1
    #determine if player is going first or not
    if colour == 'b':
        playerTurn = True
    elif colour == 'w':
        playerTurn = False
    #while game not over, keep playing
    over = False
    while not over:
        over = s.isGameOver()
        if playerTurn:
            print('Score: white',s.getScore(s.WHITE),',black',s.getScore(s.BLACK))
            print("Enter 2 numbers from 0-7 separated by a space to make a move,\nwhere the first number is the row and the second number is the column\nEnter 'q' to quit.")
            mvalid = False
            while not mvalid:
                try:
                    s.displayBoard()
                    position = input('Enter move: ')
                    if position == 'q':
                        mvalid = True
                        break
                    elif int(position[0]) > 7 or int(position[1]) > 7 or len(position) != 2:
                        raise
                    
                    position = position.replace(" ", "")
                    int(position[1])
                except:
                    print('Invalid position: out of bound.')
                else:
                    if turn % 2 == 0:
                        colour = s.WHITE
                    else:
                        colour = s.BLACK
                    mvalid = s.isPositionValid(position, colour)
                    if not s.isPositionValid(position, colour):
                        print("Invalid position: piece doesn't surround line of opponent pieces.")                    
            if position == 'q':
                over = True
                break
            s.makeMovePlayer(position)
            s.displayBoard()
            playerTurn = False
                    
        elif not playerTurn:
            print('Score: white',s.getScore(s.WHITE),',black',s.getScore(s.BLACK))
            if diff == '1':
                s.makeMoveNaive()
            elif diff == '2':
                s.makeMoveSmart()
            playerTurn = True

                
        turn += 1     
    print('Score: white',s.getScore(s.WHITE),',black',s.getScore(s.BLACK))
    print('Game Over!')
class Reversi:
    WHITE = "w"
    BLACK = "b"
    EMPTY = "."
    SIZE = 8

    def __init__(self):
        self.playerColour = None
        self.computerColour = None
        self.gameBoard = []

    """
    Functionality:
        Create the game state so players can play again
    Parameters: 
        None
    """
    def newGame(self):
        self.gameBoard = [['.' for i in range(self.SIZE)] for n in range(self.SIZE)]
        middle = int(self.SIZE/2)
        self.gameBoard[middle-1][middle-1] = 'w'
        self.gameBoard[middle-1][middle] = 'b'
        self.gameBoard[middle][middle-1] = 'b'
        self.gameBoard[middle][middle] = 'w'
        return


    """
    Functionality:
        Return the score of the player
    Parameters:
        colour: The colour of the player to get the score for 
                Use BLACK or 'b' for black, WHITE or 'w' for white
    """
    def getScore(self, colour):
        #count all tiles of given colour in board
        score = 0
        for i in self.gameBoard:
            for n in i:
                if n == colour:
                    score += 1
        return score


    """
    Functionality:
        Set the colour for the human player to the designated colour, as well as the computer will haev the other colour
    Parameters:
        colour: The colour of the player the user wants to play as 
                Use BLACK or 'b' for black, WHITE or 'w' for white
    """
    def setPlayerColour(self, colour):
        #set player colour
        self.playerColour = colour
        if self.playerColour == 'w':
            self.computerColour = self.BLACK
        else:
            self.computerColour = self.WHITE


    """
    Functionality:
        Print out the current board state
        The index of the rows and columns should be on the left and top.
        See the sample output for details
    Parameters: 
        None
    """
    def displayBoard(self):
        print('  0 1 2 3 4 5 6 7')
        for i in range(self.SIZE):
                    print(i,' '.join(self.gameBoard[i]))        
        return 


    """
    Functionality:
        Return true if the input position 'position' is valid for the given player 'colour' to make
    Parameters: 
        position -> A list [i,j] where i is the row and j is the column
        colour: The colour that is making the move 
                Use BLACK or 'b' for black, WHITE or 'w' for white
    """
    def isPositionValid(self, position, colour):
        
        revBoard = []
        board = self.gameBoard
        x = int(position[1])
        y = int(position[0])
        if self.gameBoard[y][x] != '.':
            return False
        #temporarily set tile to given colour
        self.gameBoard[y][x] = colour
        #get reversed board for testing
        for i in self.gameBoard:
            n = list(reversed(i))
            revBoard.append(n)        
        #get horizontal list from x position
        hlist = self.gameBoard[y]
        #get vertical list
        vlist = []
        for i in range(len(self.gameBoard)):
            vlist.append(self.gameBoard[i][x])
        #get right diagonal list
        rdiag = list(self.rdiagonal(board,x,y))
        #get left diagonal list
        ldiag = list(self.ldiagonal(revBoard,(7-x),y))
        #check if given tile is valid
        if len(self.process(hlist,colour,x)) != 0 or len(self.process(vlist,colour,y)) != 0 or len(self.dprocess(rdiag,colour, x,y)) != 0 or len(self.dprocess(ldiag,colour, 7-x,y)) != 0:
            self.gameBoard[y][x] = '.'
            return True        
        elif len(self.process(hlist,colour,x)) == 0 or len(self.process(vlist,colour,y)) == 0 or len(self.dprocess(rdiag,colour,x,y)) == 0 or len(self.dprocess(ldiag,colour,7-x,y)) == 0:
            self.gameBoard[y][x] = '.'
            return False            
        
        

    """
    Functionality:
        Return true if the game is over, false otherwise
        The game is over if any player cannot make a move, no matter whose turn it is
    Parameters: 
        None
    Note: 
        Skipping is not allowed
    """
    def isGameOver(self):
        #if no tiles are valid for either human or computer, game is over
        available = 0
        for i in range(len(self.gameBoard)):
            for n in range(len(self.gameBoard[i])):
                if self.gameBoard[i][n] == '.':
                    if self.isPositionValid([i,n],self.computerColour) or self.isPositionValid([i,n],self.computerColour):
                        available += 1
        if available == 0:
            return True


    """
    Functionality:
        Make the given move for the human player, and capture any pieces
        If you assume the move is valid, make sure the validity is checked before calling
    Parameters: 
        position -> A list [i,j] where i is the row and j is the column
        colour: The colour that is making the move 
                Use BLACK or 'b' for black, WHITE or 'w' for white
    """
    def makeMovePlayer(self, position):
        revBoard = []
        board = self.gameBoard
        x = int(position[1])
        y = int(position[0])
        self.gameBoard[y][x] = self.playerColour
        #get reversed board
        for i in self.gameBoard:
            n = list(reversed(i))
            revBoard.append(n)        
        hlist = self.gameBoard[y]
        vlist = []
        for i in range(len(self.gameBoard)):
            vlist.append(self.gameBoard[i][x])
        rdiag = list(self.rdiagonal(board,x,y))
        ldiag = list(self.ldiagonal(revBoard,(7-x),y))
        #get tiles that have to be flipped
        htiles = self.process(hlist,self.playerColour,x)
        vtiles = self.process(vlist,self.playerColour,y)
        ldTiles = self.dprocess(ldiag,self.playerColour,7-x,y)
        rdTiles = self.dprocess(rdiag,self.playerColour,x,y)
        #flip tiles
        for i in htiles:
            self.gameBoard[y][i] = self.playerColour
        for i in vtiles:
            self.gameBoard[i][x] = self.playerColour
        for i in ldTiles:
            self.gameBoard[i[0]][i[1]] = self.playerColour
        for i in rdTiles:
            self.gameBoard[i[0]][i[1]] = self.playerColour




    """
    Functionality:
        Make a naive move for the computer
        This is the first valid move when scanning the board left to right, starting at the top
    Parameters: 
        None
    """
    def makeMoveNaive(self):
        possible = []
        #get possible moves from current board state
        for i in range(len(self.gameBoard)):
            for n in range(len(self.gameBoard[i])):
                if self.gameBoard[i][n] == '.':
                    if self.isPositionValid([i,n],self.computerColour):
                        possible.append([i,n])
        self.displayBoard()
        #randomize possible moves list
        shuffle(possible)
        x = possible[0][1]
        y = possible[0][0]
        revBoard = []
        board = self.gameBoard
        self.gameBoard[y][x] = self.computerColour
        for i in self.gameBoard:
            n = list(reversed(i))
            revBoard.append(n)        
        hlist = self.gameBoard[y]
        vlist = []
        for i in range(len(self.gameBoard)):
            vlist.append(self.gameBoard[i][x])
        rdiag = list(self.rdiagonal(board,x,y))
        ldiag = list(self.ldiagonal(revBoard,(7-x),y))
        #get tiles
        htiles = self.process(hlist,self.computerColour,x)
        vtiles = self.process(vlist,self.computerColour,y)
        ldTiles = self.dprocess(ldiag,self.computerColour,7-x,y)
        rdTiles = self.dprocess(rdiag,self.computerColour,x,y)
        #flip
        for i in htiles:
            self.gameBoard[y][i] = self.computerColour
        for i in vtiles:
            self.gameBoard[i][x] = self.computerColour
        for i in ldTiles:
            self.gameBoard[i[0]][i[1]] = self.computerColour
        for i in rdTiles:
            self.gameBoard[i[0]][i[1]] = self.computerColour
        print('Computer making move:',[y,x])
        self.displayBoard()


    """
    Functionality:
        Make a move for the computer which is the best move available
        This should be the move that results in the best score for the computer
    Parameters: 
        None
    """
    def makeMoveSmart(self):
        possible = []
        for i in range(len(self.gameBoard)):
            for n in range(len(self.gameBoard[i])):
                if self.gameBoard[i][n] == '.':
                    if self.isPositionValid([i,n],self.computerColour):
                        possible.append([i,n])
        scores = []
        #get best possible move
        for y,x in possible:
            revBoard = []
            board = self.gameBoard
            self.gameBoard[y][x] = self.computerColour
            for i in self.gameBoard:
                n = list(reversed(i))
                revBoard.append(n)        
            hlist = self.gameBoard[y]
            vlist = []
            for i in range(len(self.gameBoard)):
                vlist.append(self.gameBoard[i][x])
            rdiag = list(self.rdiagonal(board,x,y))
            ldiag = list(self.ldiagonal(revBoard,(7-x),y))
            
            htiles = self.process(hlist,self.computerColour,x)
            vtiles = self.process(vlist,self.computerColour,y)
            ldTiles = self.dprocess(ldiag,self.computerColour,7-x,y)
            rdTiles = self.dprocess(rdiag,self.computerColour,x,y)
            scores.append([len(htiles)+len(vtiles)+len(ldTiles)+len(rdTiles),[y,x]])
            self.gameBoard[y][x] = '.'
        #sort list so highest score is first
        scores = list(reversed(sorted(scores)))
        print(scores[0])
        x = scores[0][1][1]
        y = scores[0][1][0]
        self.gameBoard[y][x] = self.computerColour
        for i in self.gameBoard:
            n = list(reversed(i))
            revBoard.append(n)        
        hlist = self.gameBoard[y]
        vlist = []
        for i in range(len(self.gameBoard)):
            vlist.append(self.gameBoard[i][x])
        rdiag = list(self.rdiagonal(board,x,y))
        ldiag = list(self.ldiagonal(revBoard,(7-x),y))
        
        htiles = self.process(hlist,self.computerColour,x)
        vtiles = self.process(vlist,self.computerColour,y)
        ldTiles = self.dprocess(ldiag,self.computerColour,7-x,y)
        rdTiles = self.dprocess(rdiag,self.computerColour,x,y) 
        for i in htiles:
            self.gameBoard[y][i] = self.computerColour
        for i in vtiles:
            self.gameBoard[i][x] = self.computerColour
        for i in ldTiles:
            self.gameBoard[i[0]][i[1]] = self.computerColour
        for i in rdTiles:
            self.gameBoard[i[0]][i[1]] = self.computerColour        
        print('Computer making move:',[y,x])
        self.displayBoard()        
        return
    
    def process(self,l,colour, s):
        #process horizontal or vertical lines
        if colour == 'b':
            other = 'w'
        else:
            other = 'b'        
        #l is list, rl is reversed list, and ri and li are indexes of to be flipped tiles
        rl = list(reversed(l))
        rq = []
        ri = []
        lq = []
        li = []
        #traverse list forward from starting index
        for i in range(s+1,len(l)):
            if l[i] == colour:
                break
            elif l[i] == other or '.':
                rq.append(l[i])
                ri.append(i)
        
        if l[-1] == other:
            ri.clear()
        elif set(rq) != {other}:
            ri.clear()
        #traverse backwards (reversed list) from starting index
        for i in range(len(rl)-(s),len(rl)):
            if rl[i] == colour:
                break
            elif rl[i] == other or rl[i] == '.':
                lq.append(rl[i])
                li.append(len(l)-i-1)    
        
        if rl[-1] == other:
            li.clear()
        elif set(lq) != {other}:
            li.clear()
        ind = ri + li
        return ind

    def dprocess(self,l,colour, x, y):
        #process diagonal lists
        dlist = []
        if colour == 'b':
            other = 'w'
        else:
            other = 'b'        
        
        for i in l:
            dlist.append(i[0])
        idx = None
        #get starting position for diagonal lists
        if x < y:
            row = y-x
            idx = y-row

        elif y < x:
            idx = min(x,y)
        elif x == y:
            idx = x

        
        rl = list(reversed(dlist))
        rq = []
        ri = []
        lq = []
        li = []
        
        try:
            for i in range(idx+1,len(dlist)):
                if dlist[i] == colour:
                    break
                elif dlist[i] == other or '.':
                    rq.append(dlist[i])
                    ri.append(i)
            
            if dlist[-1] == other:
                ri.clear()
            elif set(rq) != {other}:
                ri.clear()
            
            for i in range(len(rl)-(idx),len(rl)):
                if rl[i] == colour:
                    break
                elif rl[i] == other or rl[i] == '.':
                    lq.append(rl[i])
                    li.append(len(l)-i-1)    
            
            if rl[-1] == other:
                li.clear()
            elif set(lq) != {other}:
                li.clear()
            ind = ri + li
            final = []
            for i in ind:
                final.append(l[i][1])
            return final
        except:
            return []

    
    def rdiagonal(self,l, x, y):
        #returns right diagonal list
        #x
        row = max((y - x, 0))
        #y
        col = max((x - y, 0))
        while row < len(l) and col < len(l[row]):
            yield l[row][col],[row,col]
            row += 1
            col += 1
    
    def ldiagonal(self,l, x, y):
        #get left diagonal list
        #x
        row = max((y - x, 0))
        #y
        col = max((x - y, 0))
        while row < len(l) and col < len(l[row]):
            yield l[row][col],[row,(7 - col)]
            row += 1
            col += 1    
main()