
import maestro
from random import randint

def eye_position_random():
	servo = maestro.Controller(ttyStr="/dev/ttyACM1")
	servo.setAccel(0,35)
	servo.setSpeed(0,100)
	servo.setAccel(1,25)
	servo.setSpeed(1,20)

	servo.setTarget(1, randint(5760, 6100))
	servo.setTarget(0, randint(5000, 7000))
	servo.close()

def eye_position_default():
	servo = maestro.Controller(ttyStr="/dev/ttyACM1")
	servo.setAccel(0,15)
	servo.setSpeed(0,10)
	servo.setAccel(1,25)
	servo.setSpeed(1,10)

	servo.setTarget(1, 5960)
	servo.setTarget(0, 6000)
	servo.close()

def eye_position_open():
	servo = maestro.Controller(ttyStr="/dev/ttyACM1")
	servo.setAccel(0,15)
	servo.setSpeed(0,10)
	servo.setAccel(1,25)
	servo.setSpeed(1,10)

	servo.setTarget(1, 5000)
	servo.setTarget(0, 6000)

	print(servo.getMin(1))
	print(servo.getMax(1))
	servo.close()

def eye_position_script(script):

	servo = maestro.Controller(ttyStr="/dev/ttyACM1")
	if "oh, its you" in script:
		servo.runScriptSub(2)
		servo.close()
		return True;
	elif "it's been a long time" in script:
		servo.runScriptSub(1)
		servo.close()
		return True;
	elif "how have you been" in script:
		servo.runScriptSub(0)
		servo.close()
		return True;
	
	return False;
