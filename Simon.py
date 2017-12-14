## Written by Ben Fritzeen
## 12/11/2017
## Simon game to be used in PiDay

import random
import time

class Simon:
    def __init__(self):
        self.colorList = []

    def addColor(self):
        rand = random.randint(0, 3)
        if rand == 0:
            self.colorList.append('G')
        elif rand == 1:
            self.colorList.append('R')
        elif rand == 2:
            self.colorList.append('Y')
        else:
            self.colorList.append('B')

    def currentOrder(self):
        displayString = ""
        for i in range(len(self.colorList)):
            displayString += self.colorList[i]
        return displayString

    def isCorrect(self, string):
        for i in range(len(self.colorList)):
            if self.colorList[i].upper() != string[i].upper():
                return False
        return True

