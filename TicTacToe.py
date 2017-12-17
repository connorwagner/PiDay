## Written by Ben Fritzeen
## 12/11/2017
## TicTacToe

class TicTacToe:

    ## 1: X, 2: Y
    def __init__(self):
        self.gameBoard = []
        self.spotsUsed = 0
        self.recentState = 1
        self.recentCol = 0
        self.recentRow = 0
        self.winner = -1

        for i in range(3):
            self.gameBoard.append([0, 0, 0])

    def getSpotState(self, row, col):
        return self.gameBoard[row][col]

    def setSpotState(self, row, col, state):
        self.gameBoard[row][col] = state
        self.spotsUsed += 1

    def getNumSpotsLeft(self):
        return 9 - self.spotsUsed

    def whoseTurn(self):
        if self.getNumSpotsLeft() % 2 == 0:
            return 2
        else:
            return 1

    def isWinner(self, row, col, state):
        if self.checkForThree(row, col, state):
            self.winner = state
            return True

    def checkForThree(self, row, col, state):
        if self.checkLeftRight(row, col, state):
            return True
        elif self.checkUpDown(row, col, state):
            return True
        elif self.checkUpRightDownLeft(row, col, state):
            return True
        elif self.checkDownRightUpLeft(row, col, state):
            return True
        else:
            return False

    def checkDownRightUpLeft(self, row, col, state):
        connectCtr = 1
        ctr = 1
        while (row + ctr != 3 and col + ctr != 3):
            if connectCtr == 3:
                return True
            if self.gameBoard[row + ctr][col + ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        ctr = 1
        while (row - ctr != -1 and col - ctr != -1):
            if connectCtr == 3:
                return True
            if self.gameBoard[row - ctr][col - ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        if connectCtr == 3:
            return True
        else:
            return False

    def checkUpRightDownLeft(self, row, col, state):
        connectCtr = 1
        ctr = 1
        while (row + ctr != 3 and col - ctr != -1):
            if connectCtr == 3:
                return True
            if self.gameBoard[row + ctr][col - ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        ctr = 1
        while (row - ctr != -1 and col + ctr != 3):
            if connectCtr == 3:
                return True
            if self.gameBoard[row - ctr][col + ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        if connectCtr == 3:
            return True
        else:
            return False

    def checkUpDown(self, row, col, state):
        connectCtr = 1
        for downRow in range(row + 1, 3):
            if connectCtr == 3:
                return True
            if self.gameBoard[downRow][col] == state:
                connectCtr += 1
            else:
                break
        for upRow in range(row - 1, -1, -1):
            if connectCtr == 3:
                return True
            if self.gameBoard[upRow][col] == state:
                connectCtr += 1
            else:
                break
        if connectCtr == 3:
            return True
        return False

    def checkLeftRight(self, row, col, state):
        connectCtr = 1
        for rightCol in range(col + 1, 3):
            if connectCtr == 3:
                return True
            if self.gameBoard[row][rightCol] == state:
                connectCtr += 1
            else:
                break
        for leftCol in range(col - 1, -1, -1):
            if connectCtr == 3:
                return True
            if self.gameBoard[row][leftCol] == state:
                connectCtr += 1
            else:
                break
        if connectCtr == 3:
            return True
        return False

    def playerMove(self, row, col, state):
        self.setMostRecent(row, col, state)
        self.setSpotState(row, col, state)

    def setMostRecent(self, row, col, state):
        self.recentState = state
        self.recentCol = col
        self.recentRow = row

    def displayBoard(self):
        for i in range(3):
            print(self.gameBoard[i])


