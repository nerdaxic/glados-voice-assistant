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
	line = line.replace("°C", "degrees celcius")
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
	
	# https://glados.2022.us/synthesize/
	text = urllib.parse.quote(cleanTTSLine(line))
	TTSCommand = 'curl -L --retry 5 --get --fail -o '+synthFolder+cleanTTSFile(line)+' https://glados.2022.us/synthesize/'+text

	print(TTSCommand) 
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