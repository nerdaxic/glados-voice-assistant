import os
import subprocess
import pyaudio
import wave
from random import randint
import _thread as thread
from threading import Timer
from gladosSerial import *
from gladosServo import *
import sys
import urllib.parse
import re
import json
import random
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')
from playsound import playsound as ps

synthFolder = os.getenv('TTS_SAMPLE_FOLDER') + "/"

def playFile(filename):
	ps(filename)
	

# Turns units etc into speakable text
def cleanTTSLine(line):
	line = line.replace("°C", "degrees")
	line = line.replace("°", "degrees")
	line = line.replace("hPa", "hectopascals")
	line = line.replace("% (RH)", "percent")
	line = line.replace("g/m³", "grams per cubic meter")
	line = line.replace("sauna", "incinerator")
	line = line.replace("'", "")
	line = line.lower()

	if re.search("-\d", line):
		line = line.replace("-", "negative ")
	
	return line

# Cleans filename for the sample
def cleanTTSFile(line):
	filename = "GLaDOS-tts-"+cleanTTSLine(line).replace(" ", "-")
	filename = filename.replace("!", "")
	filename = filename.replace("°c", "degrees celcius")
	filename = filename.replace(",", "")+".wav"

	return filename

# Return the path of a TTS sample if found in the library
def checkTTSLib(line):
	line = cleanTTSLine(line)
	filename = cleanTTSFile(line)

	if os.path.isfile(synthFolder+filename):
		return synthFolder+filename
	else:
		return False

# Get GLaDOS TTS Sample over the online API
def fetchTTSSample(line):
		
	# Use local TTS engine from https://github.com/NeonGeckoCom/neon-tts-plugin-glados
	text = urllib.parse.quote(cleanTTSLine(line))
	TTSCommand = 'curl -L --retry 5 --get --fail -o '+synthFolder+cleanTTSFile(line)+' '+os.getenv('TTS_ENGINE_URL')+''+text

	setEyeAnimation("wait")
	TTSResponse = os.system(TTSCommand)

	if(TTSResponse == 0):
		print('Success: TTS sample "'+line+'" fetched')
		setEyeAnimation("idle")
		return True
	else:
		# Complain about speech synthesis core
		setEyeAnimation("angry")
		speak("My speech synthesiser core is offline.")
		return False


# Speak out the line
def speak(line):
	file = checkTTSLib(line)

	# Check if file exists
	if file:
		if eye_position_script(line) == False:
			eye_position_random()

		print(line)
		playFile(file)
		

	# Else generate file
	else:
	    print ("File not exist, generating...")

	    # Save line to TTS-folder
	    if(fetchTTSSample(line)):
	    	print(line)
	    	playFile(synthFolder+cleanTTSFile(line))



# Load jokes from a json file into a "playlist"
file = open("skills/glados_greetings.json")
greetings = json.load(file)

# Shuffle the list
random.shuffle(greetings)

# Global variable to make sure same greeting does not come up twice in a row
greeting_index = 0;

# Fetch the next joke from the playlist
def fetch_greeting():
	global greeting_index

	greeting = greetings[greeting_index]["greeting"]
	greeting_index += 1;

	# Loop the "playlist"	
	if(greeting_index > len(greetings)):
		greeting_index = 0
		random.shuffle(greetings)

	return greeting