#When one micro:bit changes its menu, send message to make the other one change menu as well
#Receive radio message correctly
#Check if already received
#Know what the message code means
#Activate correct function
#Code reaction to every code that might be send
#Send answer back.












#Parent code
from microbit import *

#Variable declaration and initialisation
Parent_Im = Image('99900:''90090:''99900:''90000:''90000')
menu = 'Id'
first = True
dosesAmount = 0
pin0.set_touch_mode(pin0.CAPACITIVE)
pin1.set_touch_mode(pin1.CAPACITIVE)
pin2.set_touch_mode(pin2.CAPACITIVE)

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
        if(first):
            sleep(1000)
            first = False
    #Menu used to manage sleep of child
    elif(menu == 'Sleep'):
        if(first):
            display.scroll("Sleep", 100)
            first = False
        else:
            stage = 2
            if(stage == 0):
                display.clear()
                display.show(Image('09090:''09090:''00000:''90009:''09990'))
                sleep(1000)
            elif(stage == 1):
                display.clear()
                display.show(Image('09090:''09090:''00000:''99999:''00000'))
                sleep(1000)
            elif(stage == 2):
                display.clear()
                display.show(Image('09090:''09090:''00000:''09990:''90009'))
                sleep(1000)
            elif(stage == 3):
                display.clear()
                display.show(Image('90009:''09090:''00000:''09990:''90009'))
                sleep(1000)
    #Menu used to manage milk intake
    elif(menu == 'Milk'):
        if(first):
            display.scroll("Milk doses = " + str(dosesAmount), 100)
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
        elif(menu == 'Milk'):
            menu = 'Id'
            first = True
    elif(buttonPress(2)):
        if(menu == 'Milk' and not (dosesAmount == 0)):
            dosesAmount -= 1
            first = True
    elif(buttonPress(3)):
        if(menu == 'Milk'):
            dosesAmount += 1
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
