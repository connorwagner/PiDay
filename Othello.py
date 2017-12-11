## Written by Ben Fritzeen
## 12/10/2017
## Othello game to be used in PiDay


## Instantiate game board
## 0: Empty, 1: White, 2: Black
class Othello:
    def __init__(self):
        self.gameBoard = []
        self.oneCtr = 0
        self.twoCtr = 0

        for i in range(8):
            self.gameBoard.append([0, 0, 0, 0, 0, 0, 0, 0])

    def getSpotState(self, row, col):
        return self.gameBoard[row][col]

    def setSpotState(self, row, col, state):
        self.gameBoard[row][col] = state
        if state == 1:
            self.oneCtr += 1
        elif state == 2:
            self.twoCtr += 1

    def getNumSpotsLeft(self):
        return 64 - (self.twoCtr + self.oneCtr)

    def isWinner(self):
        return 0 == self.getNumSpotsLeft()

    def whoWon(self):
        if self.isWinner:
            if self.oneCtr > self.twoCtr:
                return "Player One won!!"
            elif self.twoCtr > self.oneCtr:
                return "Player Two Won!!"
            else:
                return "It's a tie!!"
        else:
            return "No winner yet"

    def whoseTurn(self):
        if self.getNumSpotsLeft() % 2 == 0:
            return 1
        else:
            return 2

    def playerMove(self, state):
        move = input("Player " + str(state) + "'s move: ")
        while (not self.isValidMove(move)):
            print("Invalid move. Try again!")
            move = input("Player " + str(state) + "'s move: ")
        row = int(move[0])
        col = int(move[1])
        while (self.getSpotState(row, col) != 0):
            print("Spot already taken. Try again!")
            move = input("Player " + str(state) + "'s move: ")
            while (not self.isValidMove(move)):
                print("Invalid move. Try again!")
                move = input("Player " + str(state) + "'s move: ")
            row = int(move[0])
            col = int(move[1])
        self.checkForSwaps(row, col, state)
        self.setSpotState(row, col, state)

    def checkForSwaps(self, row, col, state):
        self.checkDownForSwaps(row, col, state)
        self.checkUpForSwaps(row, col, state)
        self.checkLeftForSwaps(row, col, state)
        self.checkRightForSwaps(row, col, state)
        self.checkDownRightForSwaps(row, col, state)
        self.checkDownLeftForSwaps(row, col, state)
        self.checkUpLeftForSwaps(row, col, state)
        self.checkUpRightForSwaps(row, col, state)

    def checkUpRightForSwaps(self, row, col, state):
        upRightList = []
        ctr = 1
        while (row + ctr != -1 and col + ctr != 8):
            if self.gameBoard[row - ctr][col + ctr] == state:
                if len(upRightList) != 0:
                    for spot in upRightList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[row - ctr][col + ctr] == 0:
                return
            else:
                upRightList.append([row - ctr, col + ctr])
                ctr += 1

    def checkDownLeftForSwaps(self, row, col, state):
        downLeftList = []
        ctr = 1
        while (row + ctr != 8 and col + ctr != -1):
            if self.gameBoard[row + ctr][col - ctr] == state:
                if len(downLeftList) != 0:
                    for spot in downLeftList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[row + ctr][col - ctr] == 0:
                return
            else:
                downLeftList.append([row + ctr, col - ctr])
                ctr += 1

    def checkUpLeftForSwaps(self, row, col, state):
        upLeftList = []
        ctr = 1
        while (row + ctr != -1 and col + ctr != -1):
            if self.gameBoard[row - ctr][col - ctr] == state:
                if len(upLeftList) != 0:
                    for spot in upLeftList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[row - ctr][col - ctr] == 0:
                return
            else:
                upLeftList.append([row - ctr, col - ctr])
                ctr += 1

    def checkDownRightForSwaps(self, row, col, state):
        downRightList = []
        ctr = 1
        while (row + ctr != 8 and col + ctr != 8):
            if self.gameBoard[row + ctr][col + ctr] == state:
                if len(downRightList) != 0:
                    for spot in downRightList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[row + ctr][col + ctr] == 0:
                return
            else:
                downRightList.append([row + ctr, col + ctr])
                ctr += 1

    def checkDownForSwaps(self, row, col, state):
        downList = []
        for i in range(row + 1, 8):
            if self.gameBoard[i][col] == state:
                if len(downList) != 0:
                    for spot in downList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[i][col] == 0:
                return
            else:
                downList.append([i, col])

    def checkUpForSwaps(self, row, col, state):
        upList = []
        for i in range(row - 1, -1, -1):
            if self.gameBoard[i][col] == state:
                if len(upList) != 0:
                    for spot in upList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[i][col] == 0:
                return
            else:
                upList.append([i, col])

    def checkLeftForSwaps(self, row, col, state):
        leftList = []
        for i in range(col - 1, -1, -1):
            if self.gameBoard[row][i] == state:
                if len(leftList) != 0:
                    for spot in leftList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[row][i] == 0:
                return
            else:
                leftList.append([row, i])

    def checkRightForSwaps(self, row, col, state):
        rightList = []
        for i in range(col + 1, 8):
            if self.gameBoard[row][i] == state:
                if len(rightList) != 0:
                    for spot in rightList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return
                else:
                    return
            elif self.gameBoard[row][i] == 0:
                return
            else:
                rightList.append([row, i])

    def isValidMove(self, string):
        if string.isdigit() and len(string) == 2 and ((int(string[0]) >= 0 and int(string[0]) <= 7)) and (
        (int(string[1]) >= 0 and int(string[1]) <= 7)):
            return True
        else:
            return False

    def displayBoard(self):
        for i in range(8):
            print(self.gameBoard[i])

    def gameControl(self):
        print("Enter your moves in the format of rowCol. Ex: '12' is row 1, column 2")
        while (not self.isWinner()):
            self.playerMove(self.whoseTurn())
            self.displayBoard()
        print(self.whoWon())


othello = Othello()
othello.gameControl()

