# RaspiMotor_L293D
Raspberry Pi Python code for controlling a 2WD robot chassis with the wii remote (via L293D)

This project was designed for a breadboard / cobbler breakout build of a robot chassis (no motor hat required).  The build uses the pi cobbler breakout board and an L293D dual H-bridge chip for motor control.  The chip is controlled directly using gpio pins on the pi, and uses PiGPIO for PWM speed control (enable pins).  


