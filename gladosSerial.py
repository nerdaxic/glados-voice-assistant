from gladosTTS import *
import time
import serial
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

def setEyeAnimation(animation="idle"):

	if(os.getenv('EYE_SERIAL_ENABLE') == "true"):
		
		try:
			ser = serial.Serial(
				port=os.getenv('EYE_SERIAL_PORT'),
				baudrate=os.getenv('EYE_SERIAL_RATE'),
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