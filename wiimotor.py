#!/usr/bin/python
import cwiid
import sys
import RPi.GPIO as GPIO
import pigpio
import os
import time

# BCM Pin mappings for motors
# right motor
ENABLE1 = 21
IN11 = 20
IN12 = 16

# Left motor
ENABLE2 = 26
IN21 = 19
IN22 = 13

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
    
class HBridge():
    '''
    HBridge class for controlling motor.  Initialize with pins and pigpio
    reference for PWM motoro speed control.  
    
    The chip used is a dual-HBridge L293D.  Wiring reference is located at:
    http://www.instructables.com/id/L293D-Motor-Driver-Pinout-Diagram/
    
    '''
    def __init__(self, enable, in1, in2, pig):
        self._enable = enable
        self._in1 = in1
        self._in2 = in2
        self._pig = pig
        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.output(in1, 0)
        GPIO.output(in2, 0)
        self._pig.set_mode(enable, pigpio.OUTPUT)
        self._pig.set_PWM_frequency(enable,60)
        self._pig.set_PWM_range(enable, 100)
        
    def go(self, speed=100, forward=True):
        pin1=1
        pin2=0
        if (forward is False):
            pin1=0
            pin2=1
        GPIO.output(self._in1, pin1)
        GPIO.output(self._in2, pin2)
        self._pig.set_PWM_dutycycle(self._enable, speed)
        
    def stop(self):
        GPIO.output(self._in1, 0)
        GPIO.output(self._in2, 0)
        self._pig.set_PWM_dutycycle(self._enable, 0)
    
def read_buttons(buttons):
    '''
    Response to button presses on the wiimote.  Input buttons is an integer
    that can be bit masked to identify which buttons are depressed.
    '''
    global speed
    result = ''
    left_go = False
    right_go = False
    left_fwd = True
    right_fwd = True
    left_speed = speed
    right_speed = speed
    diff_gain = 0.55
    if (buttons & WiiButtons.A):
        result += 'A-'
    if (buttons & WiiButtons.B):
        result += 'B-'
        ''' ...turbo... '''
        #diff_gain = 0.5
        left_speed = 100
        right_speed = 100
        #speed_up()
        #speed_up()
    if (buttons & WiiButtons.UP):
        ''' drive forward '''
        result += 'UP-'
        left_go = True
        right_go = True
        
        #left_motor.go(speed=speed)
        #right_motor.go(speed=speed)
    if (buttons & WiiButtons.DOWN):
        ''' drive backward '''
        result += 'DOWN-'
        left_go = True
        right_go = True
        left_fwd = False
        right_fwd = False
        #left_speed = diff_gain*speed
        #right_speed = diff_gain*speed
        #left_motor.go(forward=False, speed=speed)
        #right_motor.go(forward=False, speed=speed)
    if (buttons & WiiButtons.LEFT):
        ''' Circle left.  Depressing in conjunction with down will spin in place. '''
        result += 'LEFT-'
        right_go = True
        right_fwd = True
        left_speed = diff_gain*speed
        #right_motor.go(speed=0.8*speed)
    if (buttons & WiiButtons.RIGHT):
        ''' Circle right.  Depressing in conjunction with down will spin in place. '''
        result += 'RIGHT-'
        left_go = True
        left_fwd = True
        right_speed = diff_gain*speed
        #left_motor.go(speed=0.8*speed)
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
        left_motor.go(forward=left_fwd, speed=left_speed)
    else:
        left_motor.stop()

    if right_go:
        right_motor.go(forward=right_fwd, speed=right_speed)
    else:
        right_motor.stop()

        
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
    if ( speed >= 25):
        led |= cwiid.LED1_ON
    if ( speed >= 50):
        led |= cwiid.LED2_ON
    if ( speed >= 75):
        led |= cwiid.LED3_ON
    if ( speed >= 100):
        led |= cwiid.LED4_ON
        speed = 100
    wiimote.led = led

def speed_up():
    ''' Increase speed '''
    global speed
    if (speed <= 90):
        speed += 10;
    set_leds()

def speed_down():
    ''' Decrease speed '''
    global speed
    if ( speed >= 10):
        speed -= 10;
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
    left_motor.go()
    right_motor.go()
    time.sleep(0.25)
    left_motor.go(forward=False)
    right_motor.go(forward=False)
    time.sleep(0.25)
    left_motor.stop()
    right_motor.stop()

    # Infinite loop / press x to quit
    while not exit:
        c = sys.stdin.read(1)
        if c == 'x':
            exit = True
            
    wiimote.close()


# Setup motor controllers and other globals
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pig = pigpio.pi()
right_motor = HBridge(ENABLE1, IN11, IN12, pig)
left_motor = HBridge(ENABLE2, IN21, IN22, pig) 
wiimote = None
speed = 50

main()
