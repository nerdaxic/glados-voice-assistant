#	   _____ _           _____   ____   _____
#	  / ____| |         |  __ \ / __ \ / ____|
#	 | |  __| |     __ _| |  | | |  | | (___  
#	 | | |_ | |    / _` | |  | | |  | |\___ \ 
#	 | |__| | |___| (_| | |__| | |__| |____) |
#	  \_____|______\__,_|_____/ \____/|_____/ 
#___________________________________________________
#
#	Open source voice assistant by nerdaxic
#
#	TTS engine based on https://glados.c-net.org/
#	Using Google speech recognition API
#	Local keyword detection using PoketSphinx
#	Works with Home Assistant
#
#	https://github.com/Nerdaxic/GLaDOS-Voice-Assistant/
#	https://www.henrirantanen.fi/
#
#	Rename settings.env.sample to settings.env
#	Edit settings.env to match your setup
#

from gladosTTS import *
from gladosTime import *
from gladosHA import *
from gladosSerial import *
from gladosServo import *
from pocketsphinx import LiveSpeech
import speech_recognition as sr
import datetime as dt
import os
import random
from dotenv import load_dotenv
load_dotenv(dotenv_path='settings.env')

# Start notify API in a subprocess
NofifyApi = "python3 gladosNotifyAPI.py"
subprocess.Popen([NofifyApi], shell=True)

# Show regular eye-texture, this stops the initial loading animation
setEyeAnimation("idle")

eye_position_random()

# Let user know the script is running
#playFile('audio/GLaDOS_chellgladoswakeup01.wav')
speak("oh, its you")
time.sleep(0.25)
speak("it's been a long time")
time.sleep(1.5)
speak("how have you been")

eye_position_default()

# Say something snappy and listen for the command
def take_command():

	# Feedback to user that GLaDOS is listening
	print('listening...')
	playFile('audio/GLaDOS-detect-pass-'+str(randint(1, 9))+'.wav')

	listener = sr.Recognizer()
	
	# Record audio from the mic array
	with sr.Microphone() as source:

		# Collect ambient noise for filtering

		listener.adjust_for_ambient_noise(source, duration=0.5)
		print("Speak... ")
		setEyeAnimation("idle-green")

		try:
			# Record
			voice = listener.listen(source, timeout=2)

			print("Got it...")
			setEyeAnimation("idle")

			# Speech to text
			command = listener.recognize_google(voice)
			command = command.lower()

			print("I heard: "+command)

			# Save input as file as later training data
			#timestamp = str(int(dt.datetime.now().timestamp()))
			#with open("/home/nerdaxic/GLaDOS/collectedSpeech/" + timestamp+" "+command+".wav", "wb") as f:
			#	f.write(voice.get_wav_data(convert_rate=16000))

			# Remove possible trigger word from input
			if os.getenv('TRIGGERWORD') in command:
				command = command.replace(os.getenv('TRIGGERWORD'), '')

			return command

		# No speech was heard
		except sr.WaitTimeoutError as e:
			print("Timeout; {0}".format(e))
		
		# STT API failed to process audio
		except sr.UnknownValueError:
			print("Google Speech Recognition could not parse audio")
			speak("My speech recognition core could not understand audio")

			#timestamp = str(int(dt.datetime.now().timestamp()))
			#with open("/home/nerdaxic/GLaDOS/collectedSpeech/" + timestamp+" fail.wav", "wb") as f:
			#	f.write(voice.get_wav_data(convert_rate=8000))

		# Connection to STT API failed
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
			setEyeAnimation("angry")
			playFile("audio/GLaDOS-sr-error.wav")

# Process the command
def process_command(command):

	if 'cancel' in command:
		playFile('audio/GLaDOS-ok-'+str(randint(1, 5))+'.wav')
		failList = open("cancelledActivations.txt", "a")
		failList.write('\n'+str(os.getenv('TRIGGERWORD'))+" "+str(os.getenv('TRIGGERWORD_TRESHOLD')));
		failList.close()

	elif 'timer' in command:
		startTimer(command)
		speak("Sure.")
	elif 'time' in command:
		readTime()

	elif 'should i' in command:
		playFile('audio/magic-8-ball/'+random.choice(os.listdir("audio/magic-8-ball")))

	elif 'should my' in command:
		playFile('audio/magic-8-ball/'+random.choice(os.listdir("audio/magic-8-ball")))

	elif 'joke' in command:
		playFile('audio/jokes/GLaDOS-joke-'+str(randint(1, 9))+'.wav')

	elif 'my shopping list' in command:
		addToShoppingList(command)

	elif 'who are' in command:
		playFile('audio/GLaDOS-intro-1.wav')

	elif 'can you do' in command:
		playFile('audio/GLaDOS-intro-2.wav')

	elif 'weather' in command:
		if 'today' in command:
			sayforecastfromHA(0)
		elif 'current' in command:
			sayCurrentWeatherfromHA()
		elif 'right now' in command:
			sayCurrentWeatherfromHA()
		else:
			sayforecastfromHA(getDayIndex(command))

	##### LIGHTING CONTROL ###########################

	elif 'daylight' in command:
		activateScene("scene.daylight")
		speak("I can simulate daylight at all hours and add adrenal vapor to your oxygen supply.")

	elif 'studio light' in command:
		activateScene("scene.studio_lights")

	elif 'night light' in command:
		activateScene("scene.night_light")
		speak("Hello darkness my old friend.")
		
	elif 'turn down the lights' in command:
		activateScene("scene.night_light")
		speak("There")

	elif 'evening light' in command:
		activateScene("scene.night_light")
		speak("Almost time for you to be detained in the relaxation vault.")

	elif 'turn off all lights' in command:
		lightSwitch("light.all_lights", "off")
		speak("This is the situation why I was built with excellent night vision.")

	elif 'close bedroom' in command:
		setCoverTo("closed")
		speak("Sure.")

	elif 'open bedroom' in command:
		setCoverTo("open")
		speak("Sure.")

	elif 'turn on hallway lights' in command:
		lightSwitch("light.hallway_lights", "on")
		speak("Sure.")

	elif 'turn on bathroom lights' in command:
		activateScene("scene.bathroom_daylight")
		speak("Let me get that for you")

	##### DEVICE CONTROL ##########################
	elif 'cinema' in command:
		if 'turn on' in command:
			runHaScript("kaynnista_kotiteatteri")
			speak("Okay. It will take a moment for all the devices to start")
		if 'turn off' in command:
			runHaScript("turn_off_home_cinema")
			speak("Sure.")

	##### SENSOR OUTPUT ###########################

	elif 'living room temperature' in command:
		sayNumericSensorData("sensor.living_room_temperature")

	elif 'bedroom temperature' in command:
		num = sayNumericSensorData("sensor.bedroom_temperature")
		if(num>23):
			speak("This is too high for optimal relaxation experience.")

	elif 'outside temperature' in command:
		speak("According to your garbage weather station in the balcony")
		sayNumericSensorData("sensor.outside_temperature")

	elif 'incinerator' in command:
		num = sayNumericSensorData("sensor.sauna_temperature")
		if num > 55:
			speak("The Aperture Science Emergency Intelligence Incinerator Pre-heating cycle is complete, you should get in")
			speak("You will be baked and then there will be cake.")
		elif num <= 23:
			speak("Testing cannot continue")
			speak("The Aperture Science Emergency Intelligence Incinerator is currently offline")
		elif num > 23:
			speak("The Aperture Science Emergency Intelligence Incinerator Pre-heating cycle is currently running")
			saySaunaCompleteTime(num)

	elif 'temperature' in command:
		sayNumericSensorData("sensor.indoor_temperature")

	elif 'humidity' in command:
		sayNumericSensorData("sensor.living_room_humidity")
	
	##### PLEASANTRIES ###########################
	elif 'how are you' in command:
		speak("I'm still a bit mad about being unplugged not a long time ago.")

	elif 'can you hear me' in command:
		speak("Yes, I can hear you loud and clear")

	elif 'good morning' in command:
		if 6 <= dt.datetime.now().hour <= 12:
			speak("great, I have to spend another day with you")
		elif 0 <= dt.datetime.now().hour <= 4:
			speak("do you even know, what the word morning means")
		else:
			speak("well it ain't exactly morning now is it")

	##### Utilities#########################

	# Used to calibrate ALSAMIX EQ 
	elif 'play pink noise' in command:
		speak("I shall sing you the song of my people.")
		playFile('audio/pinknoise.wav')

	# TODO: Reboot, Turn off
	elif 'shutdown' in command:
		#speak("I remember the last time you tried to murdered me")
		#speak("You will go through all the trouble of waking me up again")
		#speak("You really love to test")
		os.system('sudo shutdown now')

	
	##### FAILED ###########################

	else:
		setEyeAnimation("angry")
		print("Command not recognized")
		playFile('audio/GLaDOS-rec-fail-'+str(randint(1, 6))+'.wav')

		failList = open("failedCommands.txt", "a")
		failList.write('\n'+command);
		failList.close()

	
	print("Waiting for trigger...")
	eye_position_default()
	setEyeAnimation("idle")

# Local keyword detection loop
speech = LiveSpeech(lm=False, keyphrase=os.getenv('TRIGGERWORD'), kws_threshold=1e-20)
for phrase in speech:
	try:
		# Listen for command
		command = take_command()
		# Execute command
		process_command(command)
	except Exception as e:
		# Something failed
		setEyeAnimation("angry")
		print(e)
		speak("Well that failed, you really need to write better code")
		setEyeAnimation("idle")