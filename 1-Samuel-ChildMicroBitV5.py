#Child Code
from microbit import *
import random

#Variable declaration and initialisation
Child_Im = Image('09990:''90000:''90000:''90000:''09990')
menu = 'Id'
first = True
milkPerDay = [10, 15, 7, 9]
day = 0
pin0.set_touch_mode(pin0.CAPACITIVE)
pin1.set_touch_mode(pin1.CAPACITIVE)
pin2.set_touch_mode(pin2.CAPACITIVE)
skip = False
skipShake = False
skipDirection = False
previousOrientation = 0
orientationChange = False
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

#What is the sound level?
def soundDetection():
    if(microphone.sound_level() >= 102 and microphone.sound_level() <= 153):
        return(1)
    elif(microphone.sound_level() >= 102 and microphone.sound_level() <= 204):
        return(2)
    elif(microphone.sound_level() >= 102 and microphone.sound_level() <= 255):
        return(3)

#How dangerous is the movement?
def moveDanger():
    global skip
    global skipShake
    global skipDirection
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
        display.show(Child_Im)
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
            soundLevel = soundDetection()
            if(soundLevel == 1):
                print("There's a little sound")
            elif(soundLevel == 2):
                print("There's too much sound")
            elif(soundLevel == 3):
                print("There's way too much sound")
            #Movement stuff
            moveLevel = moveDanger()
            if(moveLevel == 1):
                print("baby is moving")
            elif(moveLevel == 2):
                print("Baby has been shaken")
            elif(moveLevel == 3):
                print("Baby is falling")
            #Temperature stuff
            degrees = temperature()
            degreesDanger = 0
            if(degrees <= 5):
                degreesDanger = -2
                print("Baby is in danger of hypothermia")
            elif(degrees <= 15):
                degreesDanger = -1
                print("It's getting too cold")
            elif(degrees >= 27):
                degreesDanger = 1
                print("It's getting too hot")
            elif(degrees >= 35):
                degreesDanger = 2
                print("Baby is in danger of hyperthermia")
            #Luminosity stuff
            lightLevel = display.read_light_level()
            if(lightLevel >= 20):
                print("It's getting bright")
            elif(lightLevel >= 70):
                print("It's getting too bright")
            #Orientation stuff
            OrientationCompass = compassOrientation()
            if(not (OrientationCompass == previousOrientation)):
                orientationChange = True
            previousOrientation = OrientationCompass
            #Sleep Alarm trigger:
            #The if-elif cases are ranked from worse to best because the baby might be in a quite environnement but have fallen.
            #So worse case has to be detected first and certainly not be outruled by something less dangerous.
            if(soundLevel == 3 or moveLevel == 2 or moveLevel == 3 or degreesDanger == -2 or degreesDanger == 2):
                print("Baby might be crying")
            elif(soundLevel == 2 or degreesDanger == -1 or degreesDanger == 1):
                print("Baby is most certainly awake")
            elif(soundLevel == 1 or moveLevel == 1 or orientationChange):
                print("Baby might be awake")
    
    #Menu used to manage milk intake
    elif(menu == 'Milk'):
        if(first):
            display.scroll("Milk doses day " + str(day - (len(milkPerDay) - 1)) + " = " + str(milkPerDay[day]), 100)
            first = False

    #Game Menu
    elif(menu == "Tetris"):
        if(first):
            display.scroll("This is the game Tetris", 100)
            sleep(750)
            display.scroll("Button A = to the left", 100)
            sleep(750)
            display.scroll("Button B = to the right", 100)
            sleep(750)
            display.scroll("Let's go!", 100)
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
