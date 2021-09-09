import os
import subprocess
import pyaudio
import wave
from random import randint
import _thread as thread
from threading import Timer
import RPi.GPIO as GPIO
from gladosSerial import *
from gladosServo import *
import sys
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

# GPIO settings to use single pin to turn amplifier circuit on and off
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(int(os.getenv('SOUND_MUTE_PIN')), GPIO.OUT)

synthFolder = os.getenv('TTS_SAMPLE_FOLDER')

def playFile(filename):

	# Defines a chunk size of 1024 samples per data frame.
	chunk = 1024  

	# Open sound file  in read binary form.
	file = wave.open(filename, 'rb')

	# Initialize PyAudio
	p = pyaudio.PyAudio()

	
	# Creates a Stream to which the wav file is written to.
	# Setting output to "True" makes the sound be "played" rather than recorded
	stream = p.open(format = p.get_format_from_width(file.getsampwidth()),
	                channels = file.getnchannels(),
	                rate = file.getframerate(),
	                output = True,
	                output_device_index = int(os.getenv('SOUND_CARD_ID')))

	# Read data in chunks
	data = file.readframes(chunk)

	# Play the sound by writing the audio data to the stream

	while True:
	    data = file.readframes(chunk)
	    if not data:
	        break
	    stream.write(data)  # to be played

	time.sleep(0.1)
	
	# Stop, Close and terminate the stream
	stream.stop_stream()
	stream.close()
	#p.terminate() for some reason uncommenting this crashes notify api
	

# Turns units etc into speakable text
def cleanTTSLine(line):
	line = line.replace("°C", "degrees celcius")
	line = line.replace("°", "degrees")
	line = line.replace("hPa", "hectopascals")
	line = line.replace("% (RH)", "percent")
	line = line.replace("g/m³", "grams per cubic meter")
	line = line.replace("sauna", "incinerator")
	line = line.lower()
	
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
	TTSCommand = 'curl -L --retry 30 --get --fail --data-urlencode "text='+cleanTTSLine(line)+'" -o "'+synthFolder+cleanTTSFile(line)+'" "https://glados.c-net.org/generate"'

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
			playFile("audio/GLaDOS-tts-error.wav")
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
		    playFile('audio/GLaDOS-wait-'+str(randint(1, 6))+'.wav')

		    # Try to get wave-file from https://glados.c-net.org/
		    # Save line to TTS-folder
		    if(fetchTTSSample(line)):
		    	playFile(synthFolder+cleanTTSFile(line))