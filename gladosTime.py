import pyaudio
import wave
import datetime as dt
from random import *
from gladosTTS import *
from threading import Timer
import re
from gladosServo import *

# Reads current time aloud
def readTime():
	timer=dt.datetime.now()
	hour = timer.strftime('%H')
	minute = timer.strftime('%M')

	print(hour+":"+minute)
	eye_position_random()
	playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/clock/hour/GLaDOS-hour-'+hour+'.wav')
	eye_position_random()
	playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/clock/minute/GLaDOS-'+minute+'.wav')
	r = str(randint(1, 4))
	eye_position_random()
	#playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/clock/time-comment/GLaDOS-general-'+str(r)+'-comment.wav')

# Start a new timer
def startTimer(command):
	command = command.replace('-', ' ')
	
	# Parse the time and context from the command
	regex = r"^set (a|the)?\s?([\D]*timer[\D]*)?(([\d]{1,3}) hour)?([\D]*([\d]{1,3}) minute)?([\D]*([\d]{1,3}) second(s)?)?( timer)?( for ([\D]+))?"
	matches = re.search(regex, command, re.MULTILINE | re.IGNORECASE)

	# Context here in a "10 minute pizza timer" would be "pizza"
	if matches:
		context = str(matches[2] or "")
		hours = int(matches[4] or 0)
		minutes = int(matches[6] or 0)
		seconds = int(matches[8] or 0)

		if matches[12]:
			context = matches[12]
		
		removal_list = ["timer","the","for", "a", "set up"]
		edit_string_as_list = context.split()
		final_list = [word for word in edit_string_as_list if word not in removal_list]
		context = ' '.join(final_list)

		if context:
			if not checkTTSLib(context):
				fetchTTSSample(context, wait=False)
			context = context

		# Calculate duration to seconds
		duration = hours*3600+minutes*60+seconds

		if duration > 1:
			t = Timer(duration, timerEnd, [duration, context])
			t.start()
			print(str(duration)+" second "+context+" timer started at "+str(dt.datetime.now()))
			playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/clock/GLaDOS_Announcer_ding_on.wav')
	else:
		speak("I didn't understand the duration you wanted the timer for")

# Run this when the timer ends
def timerEnd(duration, context=""):
	playFile(os.path.dirname(os.path.abspath(__file__))+'/audio/clock/GLaDOS_Announcer_ding_off.wav')

	# Did timer have context or was it generic?
	if context:
		print("Timer for "+context+" has ended")

		if not checkTTSLib(context):
			# No words to describe context, general response
			speak("the time is up")
		else:
			# Context is known, "pizza is running out of time"
			speak(context)
			speak("is running out of time")
	else:
		# General response
		print (str(duration)+" second timer ended "+str(dt.datetime.now()))
		speak("the time is up")