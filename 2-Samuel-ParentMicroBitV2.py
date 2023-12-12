#When one micro:bit changes its menu, send message to make the other one change menu as well
#Receive radio message correctly
#Check if already received
#Know what the message code means
#Activate correct function
#Code reaction to every code that might be send
#Send answer back.











#Parent code
from microbit import *
import random
import radio

#Variable declaration and initialisation
Parent_Im = Image('99900:''90090:''99900:''90000:''90000')
menu = 'Id'
first = True
dosesAmount = 0
pin0.set_touch_mode(pin0.CAPACITIVE)
pin1.set_touch_mode(pin1.CAPACITIVE)
pin2.set_touch_mode(pin2.CAPACITIVE)
turningSequenceAngles = [1, 3, 5, 8]
chosenBlockIndex = 0
blockHeight = [0, 2, 1, 2, 2, 2, 1, 1, 2, 2, 1]
possibleBlocks = [[], [9, 9, 9, 0], [9, 0], [9, 9, 0, 9], [9, 9], [0, 9, 9, 9], [9, 0], [9, 9, 0, 0], [9, 0, 9, 9], [9, 9], [9, 0]]
initialMatrix = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
tempBlock = possibleBlocks[chosenBlockIndex]
startX = 0
startY = 0
mayFall = False
gameOver = 0
score = 0
gOmessage = False
matrixSleep = [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]]
matrixDelta = [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]]
text = False
radio.config(group=23, channel=2, address=0x11111111)
radio.on()
string = None
previousDanger = 0
message = [1, 0, 0]
solved = True

#displays the current state of the tetris board
def matrixAndTempBoardShow():
    global startX
    for y in range(5):
        for x in range(5):
            display.set_pixel(x, y, initialMatrix[y][x])
            if((x >= startX and x <= int(startX + (len(tempBlock) / 2) - 1))):
                if(y == startY and not (tempBlock[int(x - startX)] == 0)):
                    display.set_pixel(x, y, tempBlock[int(x - startX)])
                if(y == startY + 1 and blockHeight[chosenBlockIndex] == 2 and not (tempBlock[int(x - startX) + int(len(tempBlock) / 2)] == 0)):
                    display.set_pixel(x, y, tempBlock[int((x - startX) + int(len(tempBlock) / 2))])
    sleep(500)

#Is the tetris game over? Meaning is there a part of block that is stuck on the second row of leds?
def isGameOver():
    global gameOver
    global score
    for y in range(2):
        if(not (initialMatrix[y] == [0, 0, 0, 0, 0])):
            score -= 1
            return(1)
    return(0)

#When a line is entirely filled, we have to remove it and make all the other lines fall
def removeCompleteLines():
    global initialMatrix
    for y in range(5):
        if(initialMatrix[y] == [9, 9, 9, 9, 9]):
            initialMatrix[y] = [0, 0, 0, 0, 0]
            for h in range(y, 2, -1):
                initialMatrix[h] = initialMatrix[h - 1]
            initialMatrix[2] = [0, 0, 0, 0, 0]

#When a block has been placed, we memorise it to the board and reset the necessary variables to allow a new block to spawn on top of the game
#We also test if there are full lines to remove, and if the game is actually over.
def newBlockAddToInitMatrix():
    global initialMatrix
    global score
    global gameOver
    global gOmessage
    if(blockHeight[chosenBlockIndex] == 1):
        for x in range(startX, int(startX + (len(tempBlock) / 2))):
            if(not (tempBlock[int(x - startX)] == 0)):
                initialMatrix[startY][x] = tempBlock[int((x - startX))]
    elif(blockHeight[chosenBlockIndex] == 2):
        for y in range(2):
            for x in range(startX, int(startX + (len(tempBlock) / 2))):
                if(not (tempBlock[int(x - startX) + int(y * (len(tempBlock) / 2))] == 0)):
                    initialMatrix[startY + y][x] = tempBlock[int((x - startX) + (y*(len(tempBlock)/2)))]
    score += 1
    resetTetrisVar()
    removeCompleteLines()
    gameOver = isGameOver()
    if(gameOver):
        gOmessage = True

#For a block having a height of 1 pixel, can it fall? Meaning there isn't already a block where it wants to fall
def canFallH1():
    for x in range(startX, int(startX + (len(tempBlock) / 2))):
        if(not (initialMatrix[startY + 1][x] == 0)):
            return(0)
    return(1)

#For a block having a height of 2 pixels, can it fall? Meaning there isn't already a block where it wants to fall
def canFallH2():
    for y in range(1, -1, -1):
        for x in range(startX, int(startX + (len(tempBlock) / 2))):
            if((not (tempBlock[int((x - startX) + (y * (len(tempBlock)/2)))] == 0)) and (not (initialMatrix[startY + y + 1][x] == 0))):
                return(0)
    return(1)

#If a block can fall, then we make it.
def fall():
    global startY
    global mayFall
    if(blockHeight[chosenBlockIndex] == 1):
        if(canFallH1()):
            startY += 1
        else:
            mayFall = False
            newBlockAddToInitMatrix()
        if(startY == 4):
            mayFall = False
            newBlockAddToInitMatrix()
    elif(blockHeight[chosenBlockIndex] == 2):
        if(canFallH2() == 1):
            startY += 1
        else:
            mayFall = False
            newBlockAddToInitMatrix()
        if(startY == 3):
            mayFall = False
            newBlockAddToInitMatrix()

#after a block has been memorised to the board, we reset the necessary variables to allow a new block to spawn
def resetTetrisVar():
    global chosenBlockIndex
    global startY
    chosenBlockIndex = 0
    startY = 0

#To start a new game, we have to reset all the variables necessary to the game
def allReset():
    global chosenBlockIndex
    global blockHeight
    global possibleBlocks
    global initialMatrix
    global tempBlock
    global startX
    global startY
    global mayFall
    global gameOver
    global score
    chosenBlockIndex = 0
    blockHeight = [0, 2, 1, 2, 2, 2, 1, 1, 2, 2, 1]
    possibleBlocks = [[], [9, 9, 9, 0], [9, 0], [9, 9, 0, 9], [9, 9], [0, 9, 9, 9], [9, 0], [9, 9, 0, 0], [9, 0, 9, 9], [9, 9], [9, 0]]
    initialMatrix = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    tempBlock = possibleBlocks[chosenBlockIndex]
    startX = 0
    startY = 0
    mayFall = False
    gameOver = 0
    score = 0

#To rotate a block to the left side, we simply call the same block, but rotated, from the list that contains the indexes of those similar blocks.
def rotateLeft():
    global chosenBlockIndex
    for i, elem in enumerate(turningSequenceAngles):
        if(chosenBlockIndex == elem):
            if(i == 3):
                chosenBlockIndex = turningSequenceAngles[0]
            else:
                chosenBlockIndex = turningSequenceAngles[i + 1]
            break
    if(chosenBlockIndex == 4 or chosenBlockIndex == 9):
        chosenBlockIndex = 7
    elif(chosenBlockIndex == 7):
        chosenBlockIndex = 4

#Same than rotateLeft() but to the right
def rotateRight():
    global chosenBlockIndex
    for i, elem in enumerate(turningSequenceAngles):
        if(chosenBlockIndex == elem):
            if(i == 0):
                chosenBlockIndex = turningSequenceAngles[3]
            else:
                chosenBlockIndex = turningSequenceAngles[i - 1]
            break
    if(chosenBlockIndex == 4 or chosenBlockIndex == 9):
        chosenBlockIndex = 7
    elif(chosenBlockIndex == 9):
        chosenBlockIndex = 7

#Main function of the Tetris game
def playGame():
    global chosenBlockIndex
    global tempBlock
    global startX
    global gOmessage
    print(chosenBlockIndex)
    if(gameOver):
        if(gOmessage):
            display.scroll('Game Over, your score is ' + str(score) + '.', 100)
            sleep(500)
            display.scroll(' Press on button "A" for a new game', 100)
            sleep(500)
            gOmessage = False
        else:
            display.scroll(str(score), 50)
            sleep(500)
    else:
        if(chosenBlockIndex == 0):
            chosenBlockIndex = int(random.randint(1, len(possibleBlocks) - 1))
            tempBlock = possibleBlocks[chosenBlockIndex]
            startX = int(random.randint(0, (5 - int((len(tempBlock)) / 2))))
        matrixAndTempBoardShow()
        if(mayFall):
            fall()

def shiny():
    global first
    global matrixDelta
    global matrixSleep
    global counter
    if(first):
        for y in range(5):
            for x in range(5):
                matrixSleep[y][x] = int(random.randint(4, 9))
                matrixDelta[y][x] = (random.random() * 1.5)
        first = False
    for y in range(5):
        for x in range(5):
            matrixSleep[y][x] += matrixDelta[y][x]
            if(matrixSleep[y][x] >= 9 or matrixSleep[y][x] <= 2):
                matrixDelta[y][x] *= -1
                matrixSleep[y][x] += matrixDelta[y][x]
    for y in range(5):
        for x in range(5):
            display.set_pixel(x, y, int(matrixSleep[y][x]))
    sleep(100)

def checkMessage():
    global text
    global menu
    global solved
    global message
    message = temp
    if(menu == 'Id'):
        print()
    elif(menu == 'Sleep'):
        if(message[0] == 0):
            display.show(Image('09090:''09090:''00000:''90009:''09990'))
            print('yes')
        elif(message[0] == 1):
            print('no')
            solved = False
            if(not text):
                #Neutral face
                display.show(Image('09090:''09090:''00000:''99999:''00000'))
                sleep(300)
                text = True
            else:
                if(message[1] == 4):
                    #Baby moved
                    display.scroll("Movement", 100)
                elif(message[1] == 2):
                    #There is some sound
                    display.scroll("Sound", 100)
                elif(message[1] == 1):
                    #There is some light
                    display.scroll("Light", 100)
                text = False
        elif(message[0] == 2):
            solved = False
            if(not text):
                display.show(Image('90009:''09090:''00000:''09990:''90009'))
                sleep(300)
                text = True
            else:
                if(message[1] == 3):
                    #Temperature should be checked
                    display.scroll("Temperature", 100)
                elif(message[1] == 2):
                    #There is quite some sound
                    display.scroll("Too much sound", 100)
                text = False
        elif(message[0] == 3):
            solved = False
            if(not text):
                display.show(Image('90009:''09090:''00900:''09090:''90009'))
                sleep(300)
                text = True
            else:
                if(message[1] == 4):
                    if(message[2] == 2):
                        #Baby has been shaken
                        display.scroll("!Stop shaking!", 100)
                    elif(message[2] == 3):
                        #Baby fell down
                        display.scroll("!Baby fell!", 100)
                elif(message[1] == 3):
                    #Temperature is way off
                    display.scroll("!Freeze/Burn!", 100)
                elif(message[1] == 2):
                    #There is too much sound
                    display.scroll("!Deaf!", 100)
                elif(message[1] == 1):
                    #There is too much light
                    display.scroll("!Sun!", 100)
                text = False

def hashing(string):
	"""
	Hachage d'une chaîne de caractères fournie en paramètre.
	Le résultat est une chaîne de caractères.
	Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.

	:param (str) string: la chaîne de caractères à hacher
	:return (str): le résultat du hachage
	"""
	def to_32(value):
		"""
		Fonction interne utilisée par hashing.
		Convertit une valeur en un entier signé de 32 bits.
		Si 'value' est un entier plus grand que 2 ** 31, il sera tronqué.

		:param (int) value: valeur du caractère transformé par la valeur de hachage de cette itération
		:return (int): entier signé de 32 bits représentant 'value'
		"""
		value = value % (2 ** 32)
		if value >= 2**31:
			value = value - 2 ** 32
		value = int(value)
		return value

	if string:
		x = ord(string[0]) << 7
		m = 1000003
		for c in string:
			x = to_32((x*m) ^ ord(c))
		x ^= len(string)
		if x == -1:
			x = -2
		return str(x)
	return ""
    
def vigenere(message, key, decryption=False):
    text = ""
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        key_index = i % key_length
        #Letters encryption/decryption
        if char.isalpha():
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else : 
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            #Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        #Digits encryption/decryption
        elif char.isdigit():
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:  
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text

#What button is pressed?
def buttonPress(buttons):
    if(buttons == 1):
        if((pin_logo.is_touched()) and not (button_a.was_pressed()) and not (button_b.was_pressed()) and not (pin0.is_touched()) and not (pin1.is_touched()) and not (pin2.is_touched())):
            return (True)
    elif(buttons == 2):
        if(not (pin_logo.is_touched()) and (button_a.was_pressed()) and not (button_b.was_pressed()) and not (pin0.is_touched()) and not (pin1.is_touched()) and not (pin2.is_touched())):
            return (True)
    elif(buttons == 3):
        if(not (pin_logo.is_touched()) and not (button_a.was_pressed()) and (button_b.was_pressed()) and not (pin0.is_touched()) and not (pin1.is_touched()) and not (pin2.is_touched())):
            return (True)
    elif(buttons == 4):
        if(not (pin_logo.is_touched()) and not (button_a.was_pressed()) and not (button_b.was_pressed()) and (pin0.is_touched()) and not (pin1.is_touched()) and not (pin2.is_touched())):
            return (True)
    elif(buttons == 5):
        if(not (pin_logo.is_touched()) and not (button_a.was_pressed()) and not (button_b.was_pressed()) and not (pin0.is_touched()) and (pin1.is_touched()) and not (pin2.is_touched())):
            return (True)
    elif(buttons == 6):
        if(not (pin_logo.is_touched()) and not (button_a.was_pressed()) and not (button_b.was_pressed()) and not (pin0.is_touched()) and not (pin1.is_touched()) and (pin2.is_touched())):
            return (True)
    else:
        return False

#Main program
while(True):
    #Identifies the Be:bi as the "Parent" one by displaying a 'P'
    if(menu == 'Id'):
        display.show(Parent_Im)
    #Menu used to manage sleep of child
    elif(menu == 'Sleep', 100):
        if(first):
            display.scroll("Sleep", 100)
            first = False
        string = str(radio.receive())
        temp = [0]
        sleep(750)
        if(not(string == 'None')):
            temp = []
            for letter in string:
                temp.append(int(letter))
        if(solved == True or temp[0] > 0):
            message = temp
            print(message)
            if(message[0] == 0):
                print('0')
            elif(message[0] == 1):
                print('1')
        checkMessage()  
    #Menu used to manage milk intake
    elif(menu == 'Milk'):
        if(first):
            display.scroll("Milk doses = " + str(dosesAmount), 100)
            first = False  
    #Game Menu
    elif(menu == "Tetris"):
        if(first):
            display.scroll("Tetris", 100)
            first = False
        playGame()
    
    #Button use
    if(buttonPress(1)):
        display.clear()
        if(menu == 'Id'):
            menu = 'Sleep'
            first = True
        elif(menu == 'Sleep'):
            menu = 'Milk'
            first = True
        elif(menu == 'Milk'):
            menu = 'Id'
            first = True
        elif(menu == 'Tetris'):
            menu = 'Id'
            allReset()
            first = True
    elif(buttonPress(2)):
        if(menu == 'Sleep'):
            solved = True
        elif(menu == 'Milk' and not (dosesAmount == 0)):
            dosesAmount -= 1
            first = True
        elif(menu== 'Tetris'):
            if(gameOver):
                allReset()
            else:
                if(not (startX == 0)):
                    startX -= 1
    elif(buttonPress(3)):
        if(menu == 'Milk'):
            dosesAmount += 1
            first = True
        elif(menu == 'Tetris'):
            if(not (startX == (5 - (len(tempBlock)/2)))):
                startX += 1
    elif(buttonPress(4)):
        if(menu == 'Tetris'):
            rotateLeft()
            tempBlock = possibleBlocks[chosenBlockIndex]
    elif(buttonPress(5)):
        if(menu == 'Tetris'):
            rotateRight()
            tempBlock = possibleBlocks[chosenBlockIndex]
    elif(buttonPress(6)):
        if(menu == 'Milk'):
            display.scroll("Reset doses", 100)
            dosesAmount = 0
            first = True
            sleep(1000)
        elif(menu == 'Tetris'):
            if(gameOver):
                allReset()
            else:
                mayFall = True









