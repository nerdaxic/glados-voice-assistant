
import maestro
from random import randint

def eye_position_random():
	servo = maestro.Controller(ttyStr="/dev/ttyACM1")
	servo.setAccel(0,15)
	servo.setSpeed(0,100)
	servo.setAccel(1,25)
	servo.setSpeed(1,10)

	servo.setTarget(1, randint(5760, 6100))
	servo.setTarget(0, randint(5000, 7000))
	servo.close()

def eye_position_default():
	servo = maestro.Controller(ttyStr="/dev/ttyACM1")
	servo.setAccel(0,15)
	servo.setSpeed(0,10)
	servo.setAccel(1,25)
	servo.setSpeed(1,10)

	servo.setTarget(1, 6000)
	servo.setTarget(0, 6000)
	servo.close()