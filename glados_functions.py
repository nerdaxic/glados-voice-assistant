#!/usr/bin/python3
from glados_respeaker import *
from gladosSerial import *
from gladosServo import *
from word2number import w2n
from subprocess import call
import re
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

def started_listening():
	print("started listening")
	if(os.getenv('RESPEAKER_CONNECTED')):
		respeaker_mode("listen")

	# TODO: Add hook to send trigger to Home Assistant API

def stopped_listening():
	print("stopped listening")
	if(os.getenv('RESPEAKER_CONNECTED')):
		respeaker_mode("wait")
	
	# TODO: Add hook to send trigger to Home Assistant API

def started_speaking():
	print("started to speak")
	
	if(os.getenv('RESPEAKER_CONNECTED')):
		respeaker_pixel_ring()

	# TODO: Add hook to send trigger to Home Assistant API

def stopped_speaking():
	print("stopped speaking")
	# TODO: Add hook to send trigger to Home Assistant API

def log_failed_command(command):
	failList = open("failed_commands.txt", "a")
	failList.write('\n'+command);
	failList.close()

def set_volume(procent):
	procent = int(procent)
	if(procent >=100 ):
		procent = 100
	elif(procent <= 0):
		procent = 0

	subprocess.Popen(["amixer -D pulse sset Master "+str(procent)+"%"], shell=True)

def adjust_volume(command):
	original_command = command
	try:
		multiplier = 1

		# Descriptive words to number
		if "mute" in command:
			command = "volume 0%"
		elif "full" in command or "max" in command:
			command = "volume 100%"
		elif "half" in command:
			command = "volume 50%"
		elif "quarter" in command:
			command = "volume 25%"

		# Process either as procent or value from 0-10
		if "procent" in command or "%" in command:
			# Set volume to X procent
			regex = r"[\D\s](\d{1,3})\s?(%|procent){1}"
		else:
			# Set volume to five
			command = "volume " + str(w2n.word_to_num(command))
			regex = r"[\D\s](\d{1,3})$"
			multiplier = 10

		volume_procent = 0

		try:
			matches = re.search(regex, command, re.MULTILINE | re.IGNORECASE)

			if matches is None:
				# No number matches found
  				raise TypeError("I dont think thats a number at all.")
			else:
				volume_procent = int(matches[1])*multiplier

			if "negative" in command or "minus" in command or "-" in command:
				raise Exception("How do you think negative volume would work?")

			# Check that number is in range
			if (volume_procent < 0 or volume_procent > 100):
				raise Exception("I can only set my volume between 0 and 100%.")

			set_volume(volume_procent)

		except Exception as e:
			log_failed_command(original_command)
			return str(e)

	except Exception as e:
		log_failed_command(original_command)
		return "no idea what you meant"
	else:

		if volume_procent >= 70:
			return "I shall keep yelling at you, with a volume of "+str(volume_procent)+"%."
		elif volume_procent < 40:
			return "I will be speaking to you softly, with a volume of "+str(volume_procent)+"%."
		else:
			return "OK. Fine. I have set the volume to "+str(volume_procent)+"%."