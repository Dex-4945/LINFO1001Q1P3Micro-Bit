#Parent code
from microbit import *
import random
import radio
import music

#Variable declaration and initialisation
menu = 'Id'
first = False
milkDose = 0
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
radio.config(group=23, channel=2, address=0x11111111)
radio.on()
string = None
previousDanger = 0
message = []
solved = True
length = 0
key = 'bonjour'
ints = [0, 0, 0]
temp = [0]
firstShine = True
on = 0
test = False
testReceived = ''
newTest = ''
initialA = ''
changeMenu = False

nonce = 0
firstTest = False
testGood = False
count = 0

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
    elif(chosenBlockIndex == 7):
        chosenBlockIndex = 9

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
            display.scroll('Button "A" for a new game', 100)
            gOmessage = False
        else:
            display.scroll(str(score), 50)
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
    global firstShine
    if(firstShine):
        for y in range(5):
            for x in range(5):
                matrixSleep[y][x] = int(random.randint(4, 9))
                matrixDelta[y][x] = (random.random() * 0.25)
        firstShine = False
    for y in range(5):
        for x in range(5):
            matrixSleep[y][x] += matrixDelta[y][x]
            if(matrixSleep[y][x] >= 9 or matrixSleep[y][x] <= 2):
                matrixDelta[y][x] *= -1
                matrixSleep[y][x] += matrixDelta[y][x]
    for y in range(5):
        for x in range(5):
            display.set_pixel(x, y, int(matrixSleep[y][x]))

def checkMessage():
    global text
    global menu
    global solved
    global message
    global on
    if(menu == 'Id'):
        print()
    elif(menu == 'Sleep'):
        if(message[0] == 0 or message[0] == 1):
            shiny()
        elif(message[0] == 2):
            solved = False
            if(on <= 500):
                #sad face
                display.show(Image('09090:''09090:''00000:''09990:''90009'))
                on += 1
            elif(on <= 1000):
                display.clear()
                on += 1
            else:
                on = 0
        elif(message[0] == 3):
            solved = False
            if(on <= 500):
                #cross
                display.show(Image('90009:''09090:''00900:''09090:''90009'))
                on += 1
            elif(on <= 1000):
                display.clear()
                on += 1
            else:
                on = 0

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

def vigenere(message, key, decryption):
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

def deterFunc(seed):
    return(str(int((seed * 500) / 137)))

#Main program
while(True):
    #Identifies the Be:bi as the "Parent" one by displaying a 'P'
    if(menu == 'Id'):
        if(count <= 500):
            display.show(Image('99900:''90090:''99900:''90000:''90000'))
            if(testGood == False):
                count = 0
        elif(testGood and count >= 500):
            display.show(Image('00000:''00009:''00090:''90900:''09000'))
            if(count >= 1000):
                count = 0
        count += 1
        testReceived = str(radio.receive())
        if(not (testReceived == 'None') and firstTest == False):
            testReceived = testReceived.split('|')
            print(testReceived)
            if(vigenere(testReceived[0], key, True) == '0x01'):
                print('yes')
                testReceived = testReceived[2].split(':')
                #testReceived will now contain 'A'
                testReceived = int(vigenere(testReceived[1], key, True))
                #initialA will now contain F(A) as a string
                initialA = deterFunc(testReceived)
                #Hash send
                testReceived = vigenere('0x01|', key, False)
                end = vigenere(hashing(initialA), key, False)
                print(hashing(initialA))
                testReceived += str(len(end) + 2)
                testReceived += '|'
                testReceived += vigenere(nonce, key, False)
                testReceived += ':'
                testReceived += end
                radio.send(testReceived)
                print(testReceived)
                firstTest = True
        elif(not (testReceived == 'None') and firstTest == True):
            testReceived = testReceived.split('|')
            if(vigenere(testReceived[0], key, True) == '0x02'):
                testReceived = testReceived[2].split(':')
                #testReceived will now contain the message
                testReceived = int(vigenere(testReceived[1], key, True))
                if(testReceived == 1):
                    changeMenu = True
                    testGood = True
		    key += str(deterFunc(int(randomNumber)))
                else:
                    display.scroll('Error', 100)
    
    #Menu used to manage sleep of child
    elif(menu == 'Sleep'):
        if(first):
            display.scroll("Sleep", 100)
            first = False
        string = str(radio.receive())
        temp = [0]
        if(not(string == 'None')):
            temp = []
            temp = string.split('|')
            temp[0] = vigenere(temp[0], key, True)
            if(temp[0] == '0x03'):
                temp = temp[2].split(':')
                temp[0] = vigenere(temp[0], key, True)
                temp[1] = vigenere(temp[1], key, True)
                ints = []
                for elem in temp[1]:
                    ints.append(int(elem))
        if(solved == True):
            message = ints
        checkMessage()
    #Menu used to manage milk intake
    elif(menu == 'Milk'):
        if(first):
            display.scroll("Milk doses = " + str(milkDose), 100)
            first = False  
        testReceived = str(radio.receive())
        if(not (testReceived == 'None')):
            testReceived = testReceived.split('|')
            if(vigenere(testReceived[0], key, True) == '0x04'):
                print('yes')
                answer = vigenere('0x04|', key, False)
                end = vigenere(milkDose, key, False)
                answer += str(len(str(milkDose)) + len(str(nonce)))
                answer += '|'
                answer += vigenere(nonce, key, False)
                answer += ':'
                answer += end
                radio.send(answer)
    #Game Menu
    elif(menu == "Tetris"):
        if(first):
            display.scroll("Tetris", 100)
            first = False
        playGame()
    
    #Button use
    if(pin_logo.is_touched()):
        if(changeMenu):
            display.clear()
            if(menu == 'Id'):
                menu = 'Sleep'
                first = True
            elif(menu == 'Sleep'):
                menu = 'Milk'
                first = True
            elif(menu == 'Milk'):
                menu = 'Tetris'
                first = True
            elif(menu == 'Tetris'):
                menu = 'Id'
                allReset()
                first = True
    elif(button_a.was_pressed()):
        if(menu == 'Sleep'):
            solved = True
            ints = [0, 0, 0]
        elif(menu == 'Milk' and milkDose > 0):
            milkDose -= 1
            first = True
        elif(menu== 'Tetris'):
            if(gameOver):
                allReset()                                  
            else:
                if(not (startX == 0)):
                    startX -= 1
    elif(button_b.was_pressed()):
        if(menu == 'Milk'):
            milkDose += 1
            first = True
        elif(menu == 'Tetris'):
            if(not (startX == (5 - (len(tempBlock)/2)))):
                startX += 1
    elif(pin0.is_touched()):
        if(menu == 'Tetris'):
            rotateLeft()
            tempBlock = possibleBlocks[chosenBlockIndex]
    elif(pin1.is_touched()):
        if(menu == 'Tetris'):
            rotateRight()
            tempBlock = possibleBlocks[chosenBlockIndex]
    elif(pin2.is_touched()):
        if(menu == 'Milk'):
            milkDose = 0
            first = True
        elif(menu == 'Tetris'):
            if(gameOver):
                allReset()
            else:
                mayFall = True
