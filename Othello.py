## Written by Ben Fritzeen
## 12/10/2017
## Othello game to be used in PiDay


## Instantiate game board
## 0: Empty, 1: White, 2: Black
class Othello:
    def __init__(self):
        self.gameBoard = []
        self.placeCtr = 4
        self.oneCtr = 2
        self.twoCtr = 2

        for i in range(8):
            self.gameBoard.append([0, 0, 0, 0, 0, 0, 0, 0])

    def getSpotState(self, row, col):
        return self.gameBoard[row][col]

    def setSpotState(self, row, col, state):
        self.gameBoard[row][col] = state
        self.placeCtr += 1
        if state == 1:
            self.oneCtr += 1
        elif state == 2:
            self.twoCtr += 1

    def getNumSpotsLeft(self):
        return 64 - self.placeCtr

    def isWinner(self):
        return 0 == self.getNumSpotsLeft()

    def whoseTurn(self):
        if self.getNumSpotsLeft() % 2 == 0:
            return 2
        else:
            return 1

    def playerMove(self, row, col, state):
        self.setSpotState(row, col, state)
        return self.checkForSwaps(row, col, state)

    def checkForSwaps(self, row, col, state):
        self.allSwaps = []

        self.downSwaps = self.checkDownForSwaps(row, col, state)
        self.upSwaps = self.checkUpForSwaps(row, col, state)
        self.leftSwaps = self.checkLeftForSwaps(row, col, state)
        self.rightSwaps = self.checkRightForSwaps(row, col, state)
        self.downRightSwaps = self.checkDownRightForSwaps(row, col, state)
        self.downLeftSwaps = self.checkDownLeftForSwaps(row, col, state)
        self.upRightSwaps = self.checkUpRightForSwaps(row, col, state)
        self.upLeftSwaps = self.checkUpLeftForSwaps(row, col, state)

        if self.downSwaps != None:
            for spot in self.downSwaps:
                self.allSwaps.append(spot)
        if self.upSwaps != None:
            for spot in self.upSwaps:
                self.allSwaps.append(spot)
        if self.leftSwaps != None:
            for spot in self.leftSwaps:
                self.allSwaps.append(spot)
        if self.rightSwaps != None:
            for spot in self.rightSwaps:
                self.allSwaps.append(spot)
        if self.downRightSwaps != None:
            for spot in self.downRightSwaps:
                self.allSwaps.append(spot)
        if self.downLeftSwaps != None:
            for spot in self.downLeftSwaps:
                self.allSwaps.append(spot)
        if self.upRightSwaps != None:
            for spot in self.upRightSwaps:
                self.allSwaps.append(spot)
        if self.upLeftSwaps != None:
            for spot in self.upLeftSwaps:
                self.allSwaps.append(spot)

        if state == 2:
            self.twoCtr += len(self.allSwaps)
            self.oneCtr -= len(self.allSwaps)
        else:
            self.oneCtr += len(self.allSwaps)
            self.twoCtr -= len(self.allSwaps)

        return self.allSwaps

    def checkUpRightForSwaps(self, row, col, state):
        upRightList = []
        ctr = 1
        while (row - ctr != -1 and col + ctr != 8):
            if self.gameBoard[row - ctr][col + ctr] == state:
                if len(upRightList) != 0:
                    for spot in upRightList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return upRightList
                else:
                    return []
            elif self.gameBoard[row - ctr][col + ctr] == 0:
                return []
            else:
                upRightList.append([row - ctr, col + ctr])
                ctr += 1

    def checkDownLeftForSwaps(self, row, col, state):
        downLeftList = []
        ctr = 1
        while (row + ctr != 8 and col - ctr != -1):
            if self.gameBoard[row + ctr][col - ctr] == state:
                if len(downLeftList) != 0:
                    for spot in downLeftList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return downLeftList
                else:
                    return []
            elif self.gameBoard[row + ctr][col - ctr] == 0:
                return []
            else:
                downLeftList.append([row + ctr, col - ctr])
                ctr += 1

    def checkUpLeftForSwaps(self, row, col, state):
        upLeftList = []
        ctr = 1
        while (row - ctr != -1 and col - ctr != -1):
            if self.gameBoard[row - ctr][col - ctr] == state:
                if len(upLeftList) != 0:
                    for spot in upLeftList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return upLeftList
                else:
                    return []
            elif self.gameBoard[row - ctr][col - ctr] == 0:
                return []
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
                    return downRightList
                else:
                    return []
            elif self.gameBoard[row + ctr][col + ctr] == 0:
                return []
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
                    return downList
                else:
                    return []
            elif self.gameBoard[i][col] == 0:
                return []
            else:
                downList.append([i, col])

    def checkUpForSwaps(self, row, col, state):
        upList = []
        for i in range(row - 1, -1, -1):
            if self.gameBoard[i][col] == state:
                if len(upList) != 0:
                    for spot in upList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return upList
                else:
                    return []
            elif self.gameBoard[i][col] == 0:
                return []
            else:
                upList.append([i, col])

    def checkLeftForSwaps(self, row, col, state):
        leftList = []
        for i in range(col - 1, -1, -1):
            if self.gameBoard[row][i] == state:
                if len(leftList) != 0:
                    for spot in leftList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return leftList
                else:
                    return []
            elif self.gameBoard[row][i] == 0:
                return []
            else:
                leftList.append([row, i])

    def checkRightForSwaps(self, row, col, state):
        rightList = []
        for i in range(col + 1, 8):
            if self.gameBoard[row][i] == state:
                if len(rightList) != 0:
                    for spot in rightList:
                        self.gameBoard[spot[0]][spot[1]] = state
                    return rightList
                else:
                    return []
            elif self.gameBoard[row][i] == 0:
                return []
            else:
                rightList.append([row, i])

    def displayBoard(self):
        for i in range(8):
            print(self.gameBoard[i])

