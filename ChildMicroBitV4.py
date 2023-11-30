#Child Code
from microbit import *

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

#What is the sound level?
def soundDetection():
    if(microphone.sound_level() >= 102 and microphone.sound_level() <= 153):
        return(1)
    elif(microphone.sound_level() >= 102 and microphone.sound_level() <= 204):
        return(2)
    elif(microphone.sound_level() >= 102 and microphone.sound_level() <= 255):
        return(3)

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
        
def moveDirection():
    if(accelerometer.is_gesture('up')):
        return(1)
    elif(accelerometer.is_gesture('down')):
        return(2)
    elif(accelerometer.is_gesture('face up')):
        return(3)
    elif(accelerometer.is_gesture('face down')):
        return(4)
    elif(accelerometer.is_gesture('left')):
        return(5)
    elif(accelerometer.is_gesture('right')):
        return(6)
    return(0)
        
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
            if(degrees <= 10):
                print("It's getting too cold")
            elif(degrees >= 30):
                print("It's getting too hot")
            #Luminosity stuff
            #Orientation stuff
            #Sleep Alarm trigger:
            if(moveLevel == 3):
                print("Baby is awake due to movement")
            elif(moveLevel == 2):
                print("Baby is awake due to movement")
            elif(soundLevel == 1 or moveLevel == 1):
                print("Baby might have been woken up due to noise")
            elif(soundLevel == 2):
                print("Baby most certainly has been woken up due to noise")
            elif(soundLevel == 3):
                print("Baby might be crying due to noise")
    
    #Menu used to manage milk intake
    elif(menu == 'Milk'):
        if(first):
            display.scroll("Milk doses day " + str((day + 1) - len(milkPerDay)) + " = " + str(milkPerDay[day]), 100)
            first = False
    
    #Button use
    if(buttonPress(1)):
        display.clear()
        if(menu == 'Id'):
            menu = 'Sleep'
            first = True
        elif(menu == 'Sleep'):
            menu = 'Milk'
            first = True
            #day = len(milkPerDay) - 1
            day = 1
        elif(menu == 'Milk'):
            menu = 'Id'
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
    elif(buttonPress(3)):
        if(menu == 'Milk' and day < len(milkPerDay) - 1):
            day += 1
            first = True
        elif(menu == 'Milk' and day == len(milkPerDay) - 1):
            display.clear()
            display.scroll("This is today", 100)
            display.clear()
            first = True
    elif(buttonPress(4)):
        sleep(1)
    elif(buttonPress(5)):
        sleep(1)
    elif(buttonPress(6)):
        if(menu == 'Milk'):
            display.scroll("Reset doses", 100)
            dosesAmount = 0
            first = True
            sleep(1000)
