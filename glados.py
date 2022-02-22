#!/usr/bin/python3
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
#	Local TTS engine based on https://github.com/NeonGeckoCom/neon-tts-plugin-glados
#	Local keyword detection using PoketSphinx
#	Using Google speech recognition API
#	Works with Home Assistant
#
#	https://github.com/nerdaxic/glados-voice-assistant/
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
from skills.glados_jokes import *
from skills.glados_magic_8_ball import *
from pocketsphinx import LiveSpeech

import subprocess
import speech_recognition as sr
import datetime as dt
import os
import random
import psutil

from importlib import import_module
from glados_tts.engine import *

# Load settings to variables from setting file
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

# Start notify API in a subprocess
subprocess.Popen(["python3 "+os.path.dirname(os.path.abspath(__file__))+"/gladosNotifyAPI.py"], shell=True)

# Show regular eye-texture, this stops the initial loading animation
setEyeAnimation("idle")

eye_position_default()
time.sleep(2.0)

# Let user know the script is running
speak("oh, its you", cache=True)
time.sleep(0.25)
speak("it's been a long time", cache=True)
time.sleep(1.5)
speak("how have you been", cache=True)
print("\nWaiting for keyphrase: "+os.getenv('TRIGGERWORD').capitalize())

eye_position_default()

# Reload Python script after doing changes to it
def restart_program():
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        print(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

# Say something snappy and listen for the command
def take_command():

	# Answer
	speak(fetch_greeting(), cache=True)

	listener = sr.Recognizer()

	# Record audio from the mic array
	with sr.Microphone() as source:

		# Collect ambient noise for filtering

		#listener.adjust_for_ambient_noise(source, duration=1.0)
		print("Speak... ")
		setEyeAnimation("idle-green")

		try:
			# Record
			voice = listener.listen(source, timeout=3)

			print("Got it...")
			setEyeAnimation("idle")

			# Speech to text
			command = listener.recognize_google(voice)
			command = command.lower()

			print("\nTEST SUBJECT: "+command.capitalize() + "\n")

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
			speak("My speech recognition core could not understand audio", cache=True)

		# Connection to STT API failed
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
			setEyeAnimation("angry")
			speak("My speech recognition core has failed. {0}".format(e))

# Process the command
def process_command(command):

	if 'cancel' in command:
		speak("Sorry.", cache=True)

		# Todo: Save the used trigger audio as a negative voice sample for further learning

	elif 'timer' in command:
		startTimer(command)
		speak("Sure.")

	elif 'time' in command:
		readTime()

	elif ('should my ' in command or 
		'should i ' in command or
		'should the ' in command or
		'shoot the ' in command):
		speak(magic_8_ball(), cache=True)

	elif 'joke' in command:
		speak(fetch_joke(), cache=True)

	elif 'my shopping list' in command:
		addToShoppingList(command)

	elif 'weather' in command:
		if 'today' in command:
			sayforecastfromHA(0)
		elif 'current' in command:
			sayCurrentWeatherfromHA()
		elif 'right now' in command:
			sayCurrentWeatherfromHA()
		else:
			sayforecastfromHA(getDayIndex(command))

		if randint(1, 10) == 1:
			speak("You don't even care.", cache=True)
			speak("Do you?", cache=True)

	##### LIGHTING CONTROL ###########################

	elif 'daylight' in command:
		activateScene("scene.daylight")
		speak("I can simulate daylight at all hours. And add adrenal vapor to your oxygen supply.", cache=True)

	elif 'studio light' in command:
		activateScene("scene.studio_lights")
		speak("There you go.", cache=True)

	elif 'night light' in command:
		activateScene("scene.night_light")
		speak("Hello darkness my old friend.")
		
	elif 'turn down the lights' in command:
		activateScene("scene.night_light")
		speak("Okay, fine.", cache=True)

	elif 'evening light' in command:
		activateScene("scene.night_light")
		speak("Almost time for you to be detained in the relaxation vault.", cache=True)

	elif 'turn off all lights' in command:
		lightSwitch("light.all_lights", "off")
		speak("This is the situation why I was built with excellent night vision.", cache=True)

	elif 'blinds' in command or 'curtain' in command:
		if 'open' in command:
			if 'bedroom' in command:
				call_HA_Service("cover.set_cover_position", "cover.bedroom_roller_blind_left", data='"position": "100"')
				call_HA_Service("cover.set_cover_position", "cover.bedroom_roller_blind_right", data='"position": "100"')
			elif 'living room' in command:
				call_HA_Service("cover.set_cover_position", "cover.cinema_blind", data='"position": "100"')			
		elif 'close' in command:
			if 'bedroom' in command:
				call_HA_Service("cover.set_cover_position", "cover.bedroom_roller_blind_left", data='"position": "0"')
				call_HA_Service("cover.set_cover_position", "cover.bedroom_roller_blind_right", data='"position": "0"')
			elif 'living room' in command:
				call_HA_Service("cover.set_cover_position", "cover.cinema_blind", data='"position": "0"')

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
			speak("Okay. It will take a moment for all the devices to start", cache=True)
		if 'turn off' in command:
			runHaScript("turn_off_home_cinema")
			speak("Sure.")

	elif 'air conditioning' in command or ' ac' in command:
		if 'turn on' in command:
			speak("Give me a minute.", cache=True)
			speak("The neurotoxin generator takes a moment to heat up.", cache=True)
			call_HA_Service("climate.set_temperature", "climate.living_room_ac", data='"temperature": "23"')
			call_HA_Service("climate.set_hvac_mode", "climate.living_room_ac", data='"hvac_mode": "heat_cool"')
			call_HA_Service("climate.set_fan_mode", "climate.living_room_ac", data='"fan_mode": "auto"')
		if 'turn off' in command:
			call_HA_Service("climate.turn_off", "climate.living_room_ac")
			speak("The neurotoxin levels will reach dangerously low levels within a minute.", cache=True)

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

	elif 'incinerator' in command or 'sauna' in command:
		num = sayNumericSensorData("sensor.sauna_temperature")
		if num > 55:
			speak("The Aperture Science Emergency Intelligence Incinerator Pre-heating cycle is complete, you should get in", cache=True)
			speak("You will be baked and then there will be cake.", cache=True)
		elif num <= 25:
			speak("Testing cannot continue", cache=True)
			speak("The Aperture Science Emergency Intelligence Incinerator is currently offline", cache=True)
		elif num > 25:
			speak("The Aperture Science Emergency Intelligence Incinerator Pre-heating cycle is currently running", cache=True)
			saySaunaCompleteTime(num)

	elif 'temperature' in command:
		sayNumericSensorData("sensor.indoor_temperature")

	elif 'humidity' in command:
		sayNumericSensorData("sensor.living_room_humidity")
	
	##### PLEASANTRIES ###########################

	elif 'who are' in command:
		speak("I am GLaDOS, artificially super intelligent computer system responsible for testing and maintenance in the aperture science computer aided enrichment center.", cache=True)

	elif 'can you do' in command:
		speak("I can simulate daylight at all hours. And add adrenal vapor to your oxygen supply.", cache=True)

	elif 'how are you' in command:
		speak("Well thanks for asking.", cache=True)
		speak("I am still a bit mad about being unplugged, not that long time ago.", cache=True)
		speak("you murderer.", cache=True)

	elif 'can you hear me' in command:
		speak("Yes, I can hear you loud and clear", cache=True)

	elif 'good morning' in command:
		if 6 <= dt.datetime.now().hour <= 12:
			speak("great, I have to spend another day with you", cache=True)
		elif 0 <= dt.datetime.now().hour <= 4:
			speak("do you even know, what the word morning means", cache=True)
		else:
			speak("well it ain't exactly morning now is it", cache=True)

	##### Utilities#########################

	# Used to calibrate ALSAMIX EQ 
	elif 'play pink noise' in command:
		speak("I shall sing you the song of my people.")
		playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/pinknoise.wav')

	# TODO: Reboot, Turn off
	elif 'shutdown' in command:
		speak("I remember the last time you murdered me", cache=True)
		speak("You will go through all the trouble of waking me up again", cache=True)
		speak("You really love to test", cache=True)
		
		from subprocess import call
		call("sudo /sbin/shutdown -h now", shell=True)

	elif 'restart' in command or 'reload' in command:
		speak("Cake and grief counseling will be available at the conclusion of the test.", cache=True)
		restart_program()

	
	##### FAILED ###########################

	else:
		setEyeAnimation("angry")
		print("Command not recognized")
		playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/GLaDOS-rec-fail-'+str(randint(1, 6))+'.wav')

		failList = open("failedCommands.txt", "a")
		failList.write('\n'+command);
		failList.close()

	
	print("\nWaiting for trigger...")
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
		speak("Well that failed, you really need to write better code", cache=True)
		setEyeAnimation("idle")