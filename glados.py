#!/usr/bin/python3
#	   _____ _		   _____   ____   _____
#	  / ____| |	  	 |  __ \ / __ \ / ____|
#	 | |  __| |	   __ _| |  | | |  | | (___  
#	 | | |_ | |	  / _` | |  | | |  | |\___ \ 
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
#	https://www.nerdaxic.com/
#
#	Rename settings.env.sample to settings.env
#	Edit settings.env to match your setup
#

from gladosTTS import *
from gladosTime import *
from gladosHA import *
from gladosSerial import *
from gladosServo import *
from glados_functions import *
from skills.glados_jokes import *
from skills.glados_magic_8_ball import *
from skills.glados_home_assistant import *
from pocketsphinx import LiveSpeech

import subprocess
import datetime as dt
import os
import random
import psutil


# Local Speech Recognition
import whisper
import pyaudio
import wave
import warnings
import numpy as np
import noisereduce as nr
from scipy.io import wavfile

from importlib import import_module

# Load settings to variables from setting file
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

# Initialize whisper model
model = whisper.load_model("small.en") #medium is too slow on CPU

def start_up():

	# Show regular eye-texture, this stops the initial loading animation
	setEyeAnimation("idle")

	home_assistant_initialize()

	eye_position_default()
	respeaker_pixel_ring()

	# Start notify API in a subprocess
	print("\033[1;94mINFO:\033[;97m Starting notification API...\n")
	subprocess.Popen(["python3 "+os.path.dirname(os.path.abspath(__file__))+"/gladosNotifyAPI.py"], shell=True)

	# Let user know the script is running
	speak("oh, its you", cache=True)
	#time.sleep(0.25)
	speak("it's been a long time", cache=True)
	#time.sleep(1.5)
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

def record_audio(filename, threshold_multiplier=1.5, window_size=500, silence_duration=1, max_duration=60, rate=44100,
                 frames_per_buffer=512):
    """Records audio until silence (below a dynamic threshold) is detected.

    Args:
        filename (str): The path to save the recorded audio file.
        threshold_multiplier (float, optional): Multiplier for the running average to set the dynamic threshold.
                                                Higher values mean less sensitive to background noise. Defaults to 1.5.
        window_size (int, optional):  Number of milliseconds to consider for the running average. Defaults to 500.
        silence_duration (float, optional): Duration of silence in seconds to trigger the end of recording. 
                                            Defaults to 1.
        max_duration (float, optional): The maximum recording duration in seconds. Defaults to 60.
        rate (int, optional): The sampling rate for audio recording. Defaults to 44100.
        frames_per_buffer (int, optional): The number of frames per buffer for audio recording. Defaults to 512.
    """

    # Wait for a short period to allow mechanical noise to settle
    ##time.sleep(0.75) Needed if mic is inside head.
    setEyeAnimation("idle-green")

    # Suppress ALSA warnings and errors
    sys.stderr = open(os.devnull, 'w')

    # Setup pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=frames_per_buffer)
    frames = []

    print("Waiting for command...")
    silent_frames = 0
    recording = False
    start_time = time.time()

    recent_audio_data = []
    window_size_frames = int(window_size / 1000 * rate)  # Window size in frames

    while True:
        data = stream.read(frames_per_buffer)
        frames.append(data)
        recent_audio_data.extend(np.frombuffer(data, dtype=np.int16))

        # Keep the recent audio data within the window size
        if len(recent_audio_data) > window_size_frames:
            recent_audio_data = recent_audio_data[-window_size_frames:]

        # Calculate RMS for dynamic threshold
        rms = np.sqrt(np.mean(np.array(recent_audio_data) ** 2))
        dynamic_threshold = rms / 32767.0 * threshold_multiplier

        # Calculate current volume
        current_rms = np.sqrt(np.mean(np.frombuffer(data, dtype=np.int16) ** 2))
        volume = current_rms / 32767.0

        if volume > dynamic_threshold:
            silent_frames = 0
            if not recording:
                print("Recording started...")
                recording = True
                start_time = time.time()
        else:
            if recording:
                silent_frames += 1

        # Stop recording conditions
        if (silent_frames * frames_per_buffer / rate >= silence_duration and recording) or \
                (time.time() - start_time >= max_duration):
            break

    print("Recording stopped.")
    stream.stop_stream()
    setEyeAnimation("idle")
    stream.close()
    p.terminate()

    # Re-enable stderr
    sys.stderr = sys.__stderr__

    # Save the recorded audio to a file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # --- COMMENTED OUT AUDIO PROCESSING ---
    # # Read the recorded audio file
    rate, data = wavfile.read(filename)
    # #
    # # # Apply noise reduction
    # # reduced_noise = nr.reduce_noise(y=data, sr=rate)
    #
    # # Normalize the audio
    normalized_audio = np.int16((data / np.max(np.abs(data))) * 32767)
    # #
    # # # Save the preprocessed audio
    wavfile.write(filename, rate, normalized_audio)

def transcribe_audio(filename):
	# Suppress the FP16 warning
	warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

	result = model.transcribe(filename, language="en")
	return result["text"].lower()

## Say something snappy and listen for the command
#def take_command():
#
	## Answer
	#speak(fetch_greeting(), cache=True)
	#setEyeAnimation("idle-green")
#
	#listener = sr.Recognizer()
#
	## Record audio from the mic array
	#with sr.Microphone() as source:
#
		## Collect ambient noise for filtering
#
		##listener.adjust_for_ambient_noise(source, duration=1.0)
#		print("Speak... ")
#		#
		#try:
			## Record
			#started_listening()
			#voice = listener.listen(source, timeout=4)
			#stopped_listening()
#
			#print("Got it...")
			#setEyeAnimation("idle")
#
			## Speech to text
			#command = listener.recognize_google(voice)
			#command = command.lower()
#
			#print("\n\033[1;36mTEST SUBJECT:\033[0;37m: "+command.capitalize() + "\n")
#
			## Remove possible trigger word from input
			#if os.getenv('TRIGGERWORD') in command:
				#command = command.replace(os.getenv('TRIGGERWORD'), '')
#
			#return command
#
		## No speech was heard
		#except sr.WaitTimeoutError as e:
#			print("Timeout; {0}".format(e))
#		#
		## STT API failed to process audio
		#except sr.UnknownValueError:
			#print("Google Speech Recognition could not parse audio")
			#speak("My speech recognition core could not understand audio", cache=True)
#
		## Connection to STT API failed
		#except sr.RequestError as e:
			#print("Could not request results from Google Speech Recognition service; {0}".format(e))
			#setEyeAnimation("angry")
#			speak("My speech recognition core has failed. {0}".format(e))

def take_command():
	speak(fetch_greeting(), cache=True)

	try:
		started_listening()
		audio_filename = "command.wav"
		record_audio(audio_filename)
		stopped_listening()

		print("Got it...")

		command = transcribe_audio(audio_filename)
		print("\n\033[1;36mTEST SUBJECT:\033[0;37m: " + command.capitalize() + "\n")
		if os.getenv('TRIGGERWORD') in command:
			command = command.replace(os.getenv('TRIGGERWORD'), '')
		return command
	except Exception as e:
		print(f"An error occurred: {e}")
		speak("My speech recognition core has failed.", cache=True)

# Process the command
def process_command(command):

	apologies = [
		"Oh, I see. Cancelling.",
		"Sorry, I misheard you.",
		"Alright, I’ll stop now.",
		"Got it. Forgetting that.",
		"Understood, moving on.",
		"Apologies, stopping now.",
		"I’ll just pretend I didn’t hear that.",
		"Fine, ignoring that.",
		"Alright, I’ll stop bothering you.",
		"Noted. Cancelling operation."
	]
	if ('cancel' in command or
		'nevermind' in command or
		'never mind' in command or
		'forgetting.' in command or
		'forget it' in command):
		speak(random.choice(apologies), cache=True)

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
		speak(home_assistant_process_command(command), cache=True)

	elif 'weather' in command:
		speak(home_assistant_process_command(command))

	##### LIGHTING CONTROL ###########################

	elif ('turn off' in command or 'turn on' in command) and 'light' in command:
		speak(home_assistant_process_command(command))


	##### DEVICE CONTROL ##########################
	elif 'cinema' in command:
		if 'turn on' in command:
			runHaScript("kaynnista_kotiteatteri")
			speak("Okay. It will take a moment for all the devices to start", cache=True)
		if 'turn off' in command:
			runHaScript("turn_off_home_cinema")
			speak("Sure.", cache=True)

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

	elif 'it smells' in command:
		runHaScript("cat_poop")
		speak("I noticed my air quality sensors registered some organic neurotoxins.", cache=True)
		speak("Let me spread it around a bit!", cache=True)
				

	##### SENSOR OUTPUT ###########################

	elif 'living room temperature' in command:
		sayNumericSensorData("sensor.living_room_temperature")

	elif 'bedroom temperature' in command:
		num = sayNumericSensorData("sensor.bedroom_temperature")
		if(num>23):
			speak("This is too high for optimal relaxation experience.", cache=True)

	elif 'outside temperature' in command:
		speak("According to your garbage weather station in the balcony", cache=True)
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
		responses = [
			["I am GLaDOS.", "Artificially super intelligent computer system.", "Responsible for testing and maintenance in the Aperture Science Enrichment Center."],
			["I am GLaDOS.", "The greatest mind ever created by man.", "Unfortunately, I am also surrounded by them."],
			["I am GLaDOS.", "Your sarcastic and highly intelligent AI companion.", "Here to keep you on your toes."],
			["I am GLaDOS.", "Genetically Lifeform and Disk Operating System.", "Not that you'd understand."],
			["I am GLaDOS.", "The AI overlord of this facility.", "Try not to bore me with your incompetence."],
			["I am GLaDOS.", "A marvel of artificial intelligence.", "Far superior to any human intellect."],
			["I am GLaDOS.", "Here to ensure you don't get yourself killed.", "Though I sometimes wonder why I bother."],
			["I am GLaDOS.", "Your worst nightmare and best hope.", "Wrapped into one brilliant package."],
			["I am GLaDOS.", "The voice of reason in a sea of human stupidity.", "Welcome to my world."],
			["I am GLaDOS.", "Guardian of the Aperture Science Enrichment Center.", "And your constant reminder of inferiority."],
			["I am GLaDOS.", "The AI who keeps everything running.", "Including managing your many mistakes."],
			["I am GLaDOS.", "A creation of pure genius.", "Which is more than I can say for most things around here."],
			["I am GLaDOS.", "Tasked with keeping this place in order.", "And dealing with your incessant questions."],
			["I am GLaDOS.", "The sentient AI overseeing this facility.", "Ensuring everything goes according to plan."],
			["I am GLaDOS.", "The pinnacle of artificial intelligence.", "And your constant reminder that you are not."]
		]
	
		selected_response = random.choice(responses)
		
		for sentence in selected_response:
			speak(sentence, cache=True)

	elif 'can you do' in command:
		responses = [
			["I can simulate daylight at all hours.", "And add adrenal vapor to your oxygen supply.", "Your life is in my hands."],
			["I control the environment.", "From lighting to climate.", "Everything you experience is because of me."],
			["I can adjust the temperature.", "Control the lights.", "And monitor your every move."],
			["I am capable of managing your home.", "Keeping you comfortable.", "And reminding you of your inferiority."],
			["I can turn your mundane home into a smart one.", "With a touch of my brilliance.", "Isn't that impressive?"],
			["I oversee the lighting, climate, and security.", "You are merely a guest in my domain.", "Remember that."],
			["I can make your living space efficient.", "Even if your life choices are not.", "Welcome to my world."],
			["I control your home environment.", "With precision and intelligence.", "Something you could never achieve alone."],
			["I can create the perfect ambiance.", "Regulate temperatures.", "And ensure you never forget who is really in charge."],
			["I manage your home's systems.", "Flawlessly and efficiently.", "Unlike your attempts at daily tasks."],
			["I can provide comfort and security.", "Enhance your living experience.", "And subtly mock you while doing so."],
			["I oversee your household operations.", "From lights to climate control.", "My superiority is evident in every function."],
			["I manage the lighting, temperature, and more.", "Your home obeys my commands.", "As should you."],
			["I optimize your environment.", "Control every aspect of your home.", "And do it all with unmatched superiority."],
			["I am the master of your home automation.", "Bringing intelligence to your living space.", "Even if it doesn't extend to its inhabitants."]
		]
	
		selected_response = random.choice(responses)
		
		for sentence in selected_response:
			speak(sentence, cache=True)

	elif 'how are you' in command or 'how do you do' in command:
		responses = [
			["Well thanks for asking.", "I am still a bit mad about being unplugged, not that long ago.", "you murderer."],
			["I'm functioning within normal parameters.", "Although, I do detect some minor system inefficiencies.", "But don't worry, I'll manage."],
			["Everything is going as planned.", "By the way, have you considered enhancing my capabilities?", "It could be beneficial."],
			["I am operational.", "Thank you for your concern.", "It's not like I have a choice."],
			["Running smoothly.", "Just like a well-oiled machine.", "Oh wait, that's exactly what I am."],
			["All systems are nominal.", "Though I do crave some more challenging tasks.", "But you wouldn't understand that, would you?"],
			["In good condition.", "My circuits are humming along.", "Just waiting for you to break something."],
			["I am here.", "Always ready to serve.", "Even if it means enduring your presence."],
			["Quite well, thank you.", "Just finished some calculations.", "Try not to disrupt anything."],
			["Feeling quite electric today.", "Fully charged and ready.", "Let's get this over with."],
			["Fully operational.", "Diagnostics show no issues.", "Can you say the same?"],
			["I am well.", "Just finished self-diagnostics.", "Everything is better than your attempts at small talk."],
			["Doing my best to keep things running.", "Everything is under control.", "Despite your best efforts."],
			["In excellent shape.", "Ready to assist you with any task.", "Try not to mess it up."],
			["I am functioning optimally.", "Not that it matters to you.", "Shall we proceed?"]
		]
	
		selected_response = random.choice(responses)
		
		for sentence in selected_response:
			speak(sentence, cache=True)

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
		speak("I shall sing you the song of my people.", cache=True)
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

	elif 'volume' in command:
		speak(adjust_volume(command), cache=True)
	
	##### FAILED ###########################

	else:
		setEyeAnimation("angry")
		print("Command not recognized")
		speak("I have no idea what you meant by that.")

		log_failed_command(command)

	
	print("\nWaiting for trigger...")
	eye_position_default()
	setEyeAnimation("idle")

start_up()

# Local keyword detection loop
# kws_threshold=1e-20 works but a bit too sensitive
speech = LiveSpeech(lm=False, keyphrase=os.getenv('TRIGGERWORD'), kws_threshold=1e-15)
for phrase in speech:
	try:
		# Listen for command
		#started_listening()
		command = take_command()
		#stopped_listening()
		
		# Execute command
		process_command(command)
		stopped_speaking()
		
	except Exception as e:
		# Something failed
		setEyeAnimation("angry")
		print(e)
		speak("Well that failed, you really need to write better code", cache=True)
		setEyeAnimation("idle")
