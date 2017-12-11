## Written by Ben Fritzeen
## 12/10/2017
## Connect-Four game to be used in PiDay


class ConnectFour:
    def __init__(self):

        self.gameBoard = []
        self.spotsUsed = 0
        self.winner = -1
        self.recentState = -1
        self.recentCol = 0

        for i in range(6):
            self.gameBoard.append([0, 0, 0, 0, 0, 0, 0])

    def getSpotState(self, row, col):
        return self.gameBoard[row][col]

    def setSpotState(self, col, state):
        for row in range(5, -1, -1):
            if self.gameBoard[row][col] == 0:
                self.gameBoard[row][col] = state
                self.spotsUsed += 1
                return

    def getNumSpotsLeft(self):
        return 42 - self.spotsUsed

    def whoseTurn(self):
        if self.getNumSpotsLeft() % 2 == 0:
            return 1
        else:
            return 2

    def isValidMove(self, string):
        if string.isdigit() and len(string) == 1 and int(string[0]) >= 0 and int(string[0]) <= 6:
            return True
        else:
            return False

    def isWinner(self, col, state):
        row = 0
        for lastRow in range(6):
            if self.gameBoard[lastRow][col] != 0:
                row = lastRow
                break

        if self.checkForFour(row, col, state):
            self.winner = state
            return True

    def checkForFour(self, row, col, state):
        if self.checkRightLeft(row, col, state):
            return True
        elif self.checkUpDown(row, col, state):
            return True
        elif self.checkDownLeftUpRight(row, col, state):
            return True
        elif self.checkDownRightUpLeft(row, col, state):
            return True
        else:
            return False

    def checkDownRightUpLeft(self, row, col, state):
        connectCtr = 1
        ctr = 1
        while (row + ctr != 6 and col + ctr != 7):
            if connectCtr == 4:
                return True
            if self.gameBoard[row + ctr][col + ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        ctr = 1
        while (row - ctr != -1 and col - ctr != -1):
            if connectCtr == 4:
                return True
            if self.gameBoard[row - ctr][col - ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        if connectCtr == 4:
            return True
        else:
            return False

    def checkDownLeftUpRight(self, row, col, state):
        connectCtr = 1
        ctr = 1
        while (row + ctr != 6 and col - ctr != -1):
            if connectCtr == 4:
                return True
            if self.gameBoard[row + ctr][col - ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        ctr = 1
        while (row - ctr != -1 and col + ctr != 7):
            if connectCtr == 4:
                return True
            if self.gameBoard[row - ctr][col + ctr] == state:
                connectCtr += 1
                ctr += 1
            else:
                break

        if connectCtr == 4:
            return True
        else:
            return False

    def checkUpDown(self, row, col, state):
        connectCtr = 1
        for downRow in range(row + 1, 6):
            if connectCtr == 4:
                return True
            if self.gameBoard[downRow][col] == state:
                connectCtr += 1
            else:
                break
        for upRow in range(row - 1, -1, -1):
            if connectCtr == 4:
                return True
            if self.gameBoard[upRow][col] == state:
                connectCtr += 1
            else:
                break

        if connectCtr == 4:
            return True
        else:
            return False

    def checkRightLeft(self, row, col, state):
        connectCtr = 1
        for rightCol in range(col + 1, 7):
            if connectCtr == 4:
                return True
            if self.gameBoard[row][rightCol] == state:
                connectCtr += 1
            else:
                break
        for leftCol in range(col - 1, -1, -1):
            if connectCtr == 4:
                return True
            if self.gameBoard[row][leftCol] == state:
                connectCtr += 1
            else:
                break

        if connectCtr == 4:
            return True
        else:
            return False

    def playerMove(self, state):
        move = input("Player " + str(state) + "'s move: ")
        while (not self.isValidMove(move)):
            print("Invalid move. Try again!")
            move = input("Player " + str(state) + "'s move: ")
        col = int(move[0])
        while (self.getSpotState(0, col) != 0):
            print("Column is already full! Try again!")
            move = input("Player " + str(state) + "'s move: ")
            while (not self.isValidMove(move)):
                print("Invalid move. Try again!")
                move = input("Player " + str(state) + "'s move: ")
            col = int(move[0])
        self.setSpotState(col, state)
        self.setMostRecent(col, state)

    def setMostRecent(self, col, state):
        self.recentState = state
        self.recentCol = col

    def displayBoard(self):
        for i in range(6):
            print(self.gameBoard[i])

    def gameControl(self):
        print("Enter your moves in the format of col. Ex: '2' is column 2")
        while (not self.isWinner(self.recentCol, self.recentState)):
            if (self.getNumSpotsLeft() == 0):
                print("Draw!!")
                return
            self.playerMove(self.whoseTurn())
            self.displayBoard()
        print("Player " + str(self.winner) + " Wins!!")


connectFour = ConnectFour()
connectFour.gameControl()


