import maestro
import os
from random import randint

import glados_settings
glados_settings.load_from_file()

def eye_position_random():
	if(glados_settings.settings["hardware"]["servo_controller"]["serial_enable"] == "true"):
		servo = maestro.Controller(ttyStr=glados_settings["hardware"]["servo_controller"]["serial_port"])
		servo.setAccel(0,25)
		servo.setSpeed(0,100)
		servo.setAccel(1,25)
		servo.setSpeed(1,20)

		servo.setTarget(1, randint(5760, 6100))
		servo.setTarget(0, randint(5000, 7000))
		servo.close()

def eye_position_default():
	if(glados_settings.settings["hardware"]["servo_controller"]["serial_enable"] == "true"):
		servo = maestro.Controller(ttyStr=glados_settings["hardware"]["servo_controller"]["serial_port"])
		servo.setAccel(0,15)
		servo.setSpeed(0,10)
		servo.setAccel(1,25)
		servo.setSpeed(1,10)

		servo.setTarget(1, 5960)
		servo.setTarget(0, 6000)
		servo.close()

def eye_position_open():
	if(glados_settings.settings["hardware"]["servo_controller"]["serial_enable"] == "true"):
		servo = maestro.Controller(ttyStr=glados_settings["hardware"]["servo_controller"]["serial_port"])
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
	if(glados_settings.settings["hardware"]["servo_controller"]["serial_enable"] == "true"):
		servo = maestro.Controller(ttyStr=glados_settings["hardware"]["servo_controller"]["serial_port"])
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
