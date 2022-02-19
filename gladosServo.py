import maestro
import os
from random import randint
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

def eye_position_random():
	if(os.getenv('MAESTRO_SERIAL_ENABLE') == "true"):
		servo = maestro.Controller(ttyStr=os.getenv('EYE_SERIAL_PORT'))
		servo.setAccel(0,25)
		servo.setSpeed(0,100)
		servo.setAccel(1,25)
		servo.setSpeed(1,20)

		servo.setTarget(1, randint(5760, 6100))
		servo.setTarget(0, randint(5000, 7000))
		servo.close()

def eye_position_default():
	if(os.getenv('MAESTRO_SERIAL_ENABLE') == "true"):
		servo = maestro.Controller(ttyStr=os.getenv('EYE_SERIAL_PORT'))
		servo.setAccel(0,15)
		servo.setSpeed(0,10)
		servo.setAccel(1,25)
		servo.setSpeed(1,10)

		servo.setTarget(1, 5960)
		servo.setTarget(0, 6000)
		servo.close()

def eye_position_open():
	if(os.getenv('MAESTRO_SERIAL_ENABLE') == "true"):
		servo = maestro.Controller(ttyStr=os.getenv('EYE_SERIAL_PORT'))
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
	if(os.getenv('MAESTRO_SERIAL_ENABLE') == "true"):
		servo = maestro.Controller(ttyStr=os.getenv('EYE_SERIAL_PORT'))
		servo.setAccel(0,15)
		servo.setSpeed(0,100)
		servo.setAccel(1,25)
		servo.setSpeed(1,20)

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
