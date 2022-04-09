from gladosTTS import *
import time
import serial

import glados_settings
glados_settings.load_from_file()


def setEyeAnimation(animation="idle"):

	if(glados_settings.settings["hardware"]["eye_controller"]["serial_enable"] in (True, 'true', '1', 't')):
		
		try:
			ser = serial.Serial(
				port=glados_settings.settings["hardware"]["eye_controller"]["serial_port"],
				baudrate=glados_settings.settings["hardware"]["eye_controller"]["serial_rate"],
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.EIGHTBITS,
				timeout=1
			)

			if "idle-green" in animation:
				ser.write("5".encode())
			elif "idle" in animation:
				ser.write("0".encode())
			elif "wait" in animation:
				ser.write("1".encode())
			elif "angry" in animation:
				ser.write("2".encode())
			elif "white" in animation:
				ser.write("3".encode())
			elif "dim" in animation:
				ser.write("4".encode())
			elif "idle-green" in animation:
				ser.write("5".encode())
		
		except serial.SerialException:
			#speak("It looks like some bird has stolen my eye")
			print(serial.SerialException)
			print("ERROR: Serial connection to the eye failed.")
