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

    def displayOrder(self):
        displayString = ""
        for i in range(len(self.colorList)):
            if i == len(self.colorList) - 1:
                displayString += self.colorList[i]
                break
            displayString += self.colorList[i] + ", "
        print(displayString)

    def isCorrect(self, string):
        if len(self.colorList) != len(string):
            return False
        for i in range(len(self.colorList)):
            if self.colorList[i].upper() != string[i].upper():
                return False
        return True

    def isValidEntry(self, string):
        if string.isalpha():
            return True
        return False

    def getInput(self):
        userInput = input("Enter the correct combination: ")
        while (not self.isValidEntry(userInput)):
            print("Only letters please! Try again!")
            userInput = input("Enter the correct combination: ")
        return userInput

    def gameControl(self):
        print("Welcome to Simon! You will be given 5 seconds to memorize each new order. Good luck!")
        self.addColor()
        self.displayOrder()
        time.sleep(5)
        print("\n" * 100)
        while (self.isCorrect(self.getInput())):
            print("Correct! Time to add a color!")
            self.addColor()
            self.displayOrder()
            time.sleep(5)
            print("\n" * 100)
        print("Sorry! Wrong combination ... the correct order was: ")
        self.displayOrder()
        print("Better luck next time!")

simon = Simon()
simon.gameControl()
