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
def fetchTTSSample(line, wait=True):
	
	# https://glados.c-net.org/
	#TTSCommand = 'curl -L --retry 30 --get --fail --data-urlencode "text='+cleanTTSLine(line)+'" -o "'+synthFolder+cleanTTSFile(line)+'" "https://glados.c-net.org/generate"'
	
	# Use local TTS engine from https://github.com/NeonGeckoCom/neon-tts-plugin-glados
	text = urllib.parse.quote(cleanTTSLine(line))
	TTSCommand = 'curl -L --retry 5 --get --fail -o '+synthFolder+cleanTTSFile(line)+' '+os.getenv('TTS_ENGINE_URL')+''+text

	if(wait):
		setEyeAnimation("wait")
		TTSResponse = os.system(TTSCommand)

		if(TTSResponse == 0):
			print('Success: TTS sample "'+line+'" fetched')
			setEyeAnimation("idle")
			return True
		else:
			# Complain about speech synthesis core
			setEyeAnimation("angry")
			playFile(os.path.dirname(os.path.abspath(__file__))+"/audio/GLaDOS-tts-error.wav")
			return False
	else:
		subprocess.Popen([TTSCommand], shell=True)
		return False


# Speak out the line
def speak(line):

	# Limitation of the TTS API
	if(len(line) < 255):

		file = checkTTSLib(line)

		# Check if file exists
		if file:
			if eye_position_script(line) == False:
				eye_position_random()

			playFile(file)
			print (line)

		# Else generate file
		else:
		    print ("File not exist, generating...")

		    # Play "hold on"
		    #playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/GLaDOS-wait-'+str(randint(1, 6))+'.wav')

		    # Try to get wave-file from https://glados.c-net.org/
		    # Save line to TTS-folder
		    if(fetchTTSSample(line)):
		    	playFile(synthFolder+cleanTTSFile(line))

def trigger_word_answer(id = randint(0,11)):
	if id == 0:
		return "tell me."
	elif id == 1:
		return "what do you want now."
	elif id == 2:
		return "hello."
	elif id == 3:
		return "what now."
	elif id == 4:
		return "hi again"
	elif id == 5:
		return "how are you"
	elif id == 6:
		return "what do you need."
	elif id == 7:
		return "hey there."
	elif id == 8:
		return "i am here."
	elif id == 9:
		return "leave me alone."
	elif id == 10:
		return "proceed."
	elif id == 11:
		return "yes, i see you."