#!/usr/bin/python
import cwiid
import sys
import RPi.GPIO as GPIO
import os
import time
from pololu_drv8835_rpi import motors, MAX_SPEED

# Hex masks for wii buttons
class WiiButtons():
    A     = 0x0008
    B     = 0x0004
    UP    = 0x0800
    DOWN  = 0x0400
    LEFT  = 0x0100
    RIGHT = 0x0200
    MINUS = 0x0010
    PLUS  = 0x1000
    ONE   = 0x0002
    TWO   = 0x0001
    
def read_buttons(buttons):
    '''
    Response to button presses on the wiimote.  Input buttons is an integer
    that can be bit masked to identify which buttons are depressed.
    '''
    global speed
    result = ''
    left_go = False
    right_go = False
    left_fwd = 1.0
    right_fwd = 1.0
    left_speed = speed
    right_speed = speed
    diff_gain = 0.75
    if (buttons & WiiButtons.A):
        result += 'A-'
    if (buttons & WiiButtons.B):
        result += 'B-'
        ''' ...turbo... '''
        left_speed = MAX_SPEED
        right_speed = MAX_SPEED
    if (buttons & WiiButtons.UP):
        ''' drive forward '''
        result += 'UP-'
        left_go = True
        right_go = True
        
    if (buttons & WiiButtons.DOWN):
        ''' drive backward '''
        result += 'DOWN-'
        left_go = True
        right_go = True
        left_fwd = -1.0
        right_fwd = -1.0

    if (buttons & WiiButtons.LEFT):
        ''' Circle left.  Depressing in conjunction with down will spin in place. '''
        result += 'LEFT-'
        right_go = True
        right_fwd = 1.0
        left_speed = diff_gain*speed

    if (buttons & WiiButtons.RIGHT):
        ''' Circle right.  Depressing in conjunction with down will spin in place. '''
        result += 'RIGHT-'
        left_go = True
        left_fwd = 1.0
        right_speed = diff_gain*speed

    if (buttons & WiiButtons.MINUS):
        ''' Reduce speed '''
        result += 'MINUS-'
        speed_down()
    if (buttons & WiiButtons.PLUS):
        ''' Increase speed '''
        result += 'PLUS-'
        speed_up()
    if (buttons & WiiButtons.ONE):
        result += 'ONE-'
    if (buttons & WiiButtons.TWO):
        result += 'TWO-'

    ''' On button release, bot will stop in place '''
    if left_go:
        motors.motor2.setSpeed(int(left_fwd*left_speed))
    else:
        motors.motor2.setSpeed(0)

    if right_go:
        motors.motor1.setSpeed(int(right_fwd*right_speed))
    else:
        motors.motor1.setSpeed(0)
        
    return result
        
def wiimote_callback(mesg_list, time):
    '''
    Function triggers every time a button is depressed / released
    '''
    #print('time: %f' % time)
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_BTN:
            #print('Button Report: %.4X' % mesg[1])
            print(read_buttons(mesg[1]))
            
        elif mesg[0] == cwiid.MESG_ERROR:
            print('Error message received.')

def set_leds():
    ''' Indicated speed settings with LEDs '''
    global speed
    global wiimote
    print('speed='+str(speed))
    led = 0
    if ( speed >= MAX_SPEED/4):
        led |= cwiid.LED1_ON
    if ( speed >= MAX_SPEED/2):
        led |= cwiid.LED2_ON
    if ( speed >= 3*MAX_SPEED/4):
        led |= cwiid.LED3_ON
    if ( speed >= MAX_SPEED):
        led |= cwiid.LED4_ON
        speed = MAX_SPEED
    wiimote.led = led

def speed_up():
    ''' Increase speed '''
    global speed
    if (speed < MAX_SPEED):
        speed += MAX_SPEED/10;
    set_leds()

def speed_down():
    ''' Decrease speed '''
    global speed
    if ( speed >= MAX_SPEED/10):
        speed -= MAX_SPEED/10;
    set_leds()
        
def main():

    # Connect wiimote
    print 'Put Wiimote in discoverable mode now (press 1+2)'
    
    global wiimote 
    wiimote = cwiid.Wiimote()
    wiimote.mesg_callback = wiimote_callback
    # Activate button reporting
    wiimote.rpt_mode = cwiid.RPT_BTN
    wiimote.enable(cwiid.FLAG_MESG_IFC);
    
    # Speed indicator
    set_leds()
    
    print('Ready to go.  "x" to exit.')
    exit = False
    
    # Demonstrate that motors are working
    quarter_speed = int(MAX_SPEED/4)
    motors.setSpeeds(quarter_speed, quarter_speed)
    time.sleep(0.25)
    motors.setSpeeds(-quarter_speed, -quarter_speed)
    time.sleep(0.25)
    motors.setSpeeds(0,0)

    # Infinite loop / press x to quit
    while not exit:
        c = sys.stdin.read(1)
        if c == 'x':
            exit = True
            
    wiimote.close()


# Setup motor controllers and other globals
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
wiimote = None
speed = MAX_SPEED/2

main()
