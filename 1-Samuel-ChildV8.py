#Child Code
from microbit import *
import random
import radio

#Variable declaration and initialisation
menu = 'Id'
first = True
milkPerDay = [10, 15, 7, 9]
day = 0
pin0.set_touch_mode(pin0.CAPACITIVE)
pin1.set_touch_mode(pin1.CAPACITIVE)
pin2.set_touch_mode(pin2.CAPACITIVE)
skipShake = False
previousOrientation = 0
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
max = [0, 0]
alarmSend = [0, 0, 0, 0, 0]

#What is the sound level?
def soundDetection():
    if(microphone.sound_level() >= 102 and microphone.sound_level() <= 153):
        return(1)
    elif(microphone.sound_level() >= 102 and microphone.sound_level() <= 204):
        return(2)
    elif(microphone.sound_level() >= 102 and microphone.sound_level() <= 255):
        return(3)
    return(0)

#How dangerous is the movement?
def moveDanger():
    global skipShake
    #I noticed that after a "freefall" gesture the next gesture was always "shake".
    #The use of the "fskipShake" variable prevents that right after a freefall, 
    #a shake event be triggered by making the check for "shake" be skipped for one iteration after a freefall. 
    #I do this by setting the "skipShake" variable to True when a freefall happens and by only triggering the "shake" event if "skipShake" is false. 
    #skipShake resets to False for the shake event to be triggerable duting the next iteration. 
    #So steps are: iteration 1 = freefall happens so skipShake is set to True, 
    #iteration 2 = skipShake set to True so shake event cannot happen, 
    #iteration 3 = shake event can be triggered again
    if(accelerometer.was_gesture('freefall')):
        skipShake = True
        return(3)
    elif(accelerometer.was_gesture('shake')):
        if(not (skipShake == True)):
            return(2)
        skipShake = False
    elif((accelerometer.was_gesture('up') or accelerometer.was_gesture('down') or accelerometer.was_gesture('face up') or accelerometer.was_gesture('face down') or accelerometer.was_gesture('left') or accelerometer.was_gesture('right')) and (abs(accelerometer.get_strength()) >= 1000)):
        return(1)
    return(0)

#What direction is the baby pointing towards?
def compassOrientation():
    if(compass.heading() >= 337.5 or compass.heading() <= 22.5):
        return(0)
    elif(compass.heading() <= 67.5):
        return(0.5)
    elif(compass.heading() <= 112.5):
        return(1)
    elif(compass.heading() <= 157.5):
        return(1.5)
    elif(compass.heading() <= 202.5):
        return(2)
    elif(compass.heading() <= 247.5):
        return(2.5)
    elif(compass.heading() <= 292.5):
        return(3)
    elif(compass.heading() <= 337.5):
        return(3.5)

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

def alarmSet():
    global alarmSend
    max = [0, 0]
    for i, elem in enumerate(alarmSend):
        if(not (i == 0) and elem >= max[1]):
            max[0] = i
            max[1] = elem
    messageClear = ''
    messageClear += str(alarmSend[0])
    messageClear += str(max[0])
    messageClear += str(max[1])
    print(messageClear)
    sleep(1000)
    return(messageClear)

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

#Main loop
while(True):
    #Compass calibration
    if(not (compass.is_calibrated())):
        compass.calibrate()
    
    #Identifies the Be:bi as the "Child" one by displaying a 'C'
    if(menu == 'Id'):
        display.show(Image('09990:''90000:''90000:''90000:''09990'))
        if(first):
            sleep(1000)
            first = False
    
    #Menu used to manage sleep of child
    elif(menu == 'Sleep'):
        if(first):
            display.scroll("Sleep", 100)
            first = False
        else:
            #Sound stuff
            alarmSend[2] = soundDetection()
            #Movement stuff
            alarmSend[4] = moveDanger()
            #Temperature stuff
            degrees = temperature()
            if(degrees > 15 and degrees < 27):
                alarmSend[3] = 0
            if(degrees <= 5):
                alarmSend[3] = 3
            elif(degrees <= 15):
                alarmSend[3] = 2
            elif(degrees >= 35):
                alarmSend[3] = 3
            elif(degrees >= 27):
                alarmSend[3] = 2
            #Luminosity stuff
            lightLevel = display.read_light_level()
            if(lightLevel >= 20 and lightLevel < 70):
                alarmSend[1] = 1
            elif(lightLevel >= 70):
                alarmSend[1] = 3
            else:
                alarmSend[1] = 0
            #Orientation stuff
            OrientationCompass = compassOrientation()
            if(not (OrientationCompass == previousOrientation)):
                alarmSend[4] = 1
            previousOrientation = OrientationCompass
            #Sleep Alarm trigger:
            #The if-elif cases are ranked from worse to best because the baby might be in a quite environnement but have fallen.
            #So worse case has to be detected first and certainly not be outruled by something less dangerous.
            if(alarmSend[2] == 3 or alarmSend[4] >= 2 or alarmSend[3] == 3 or alarmSend[1] == 3):
                alarmSend[0] = 3
            elif(alarmSend[2] == 2 or alarmSend[3] == 2):
                alarmSend[0] = 2
            elif(alarmSend[2] == 1 or alarmSend[4] == 1 or alarmSend[1] == 1 or alarmSend[3] == 1):
                alarmSend[0] = 1
            else:
                alarmSend[0] = 0
            radio.send(alarmSet())
    
    #Menu used to manage milk intake
    elif(menu == 'Milk'):
        if(first):
            display.scroll("Milk doses day " + str(day - (len(milkPerDay) - 1)) + " = " + str(milkPerDay[day]), 100)
            first = False

    #Game Menu
    elif(menu == "Tetris"):
        if(first):
            display.scroll("Tetris", 100)
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
            day = len(milkPerDay) - 1
        elif(menu == 'Milk'):
            menu = 'Tetris'
            first = True
        elif(menu == 'Tetris'):
            menu = 'Id'
            allReset()
            first = True
    elif(buttonPress(2)):
        if(menu == 'Milk' and day > 0):
            day -= 1
            first = True
        elif(menu == 'Milk' and day == 0):
            display.clear()
            display.scroll("No older data", 100)
            display.clear()
            first = True
        elif(menu== 'Tetris'):
            if(gameOver):
                allReset()
            else:
                if(not (startX == 0)):
                    startX -= 1
    elif(buttonPress(3)):
        if(menu == 'Milk' and day < len(milkPerDay) - 1):
            day += 1
            first = True
        elif(menu == 'Milk' and day == len(milkPerDay) - 1):
            display.clear()
            display.scroll("This is today", 100)
            display.clear()
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
            display.scroll("Reset today's doses", 100)
            dosesAmount = 0
            first = True
            sleep(1000)
        elif(menu == 'Tetris'):
            if(gameOver):
                allReset()
            else:
                mayFall = True
