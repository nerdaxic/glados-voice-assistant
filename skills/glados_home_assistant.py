#!/usr/bin/env python
from os.path import exists
import yaml
import json
import re
import requests
import datetime as dt
from subprocess import check_output
import threading
import random

# Instance & global variables
home_assistant = False
home_assistant_settings_file = "settings/home_assistant_settings.yaml"

# Initialize Home Assistant and test the connection
def home_assistant_initialize():

	global home_assistant
	global home_assistant_settings_file

	# Allow script to find the settings file if ran directly
	if (exists("../"+home_assistant_settings_file)):
		home_assistant_settings_file = "../"+home_assistant_settings_file

	# Check for Home Assistant setting YAML
	if (exists(home_assistant_settings_file)):

		# Validate and load settings
		home_assistant_validate_settings(load=True)
		home_assistant["api"]["endpoint"] = home_assistant["api"]["address"]+"/api/"

		# Test connection to Home Assistant API
		if not home_assistant_test_api():
			home_assistant = False
			exit();

	else:
		# TODO: Disable all home assistant functions
		home_assistant = False

		print("\033[1;94mINFO:\033[;97m Home Assistant not linked.")

# Returns True or False if Home Assistant API is responsive	
def home_assistant_test_api():
	# Set the endpoint where to send the request
	url = home_assistant["api"]["endpoint"]

	# Send request to home assistant and get server response
	response = check_output(["curl", "--insecure", "-i", "-X", "GET", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", url])

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if "API running." in str(response):
		print("\033[1;94mINFO:\033[;97m Successfully connected to Home Assistant API at " + home_assistant["api"]["endpoint"])
		return True
	else:
		home_assistant_process_error(response)

# Check and load the YAML settings file
def home_assistant_validate_settings(load=False):

	global home_assistant
	global home_assistant_settings_file

	# Check if YAML file exists
	if not exists(home_assistant_settings_file):
		print("\033[1;31mERROR 1:\033[1;97m "+home_assistant_settings_file+" file not found.")
		return False


	# Check if YAML is valid and load it to RAM
	with open(home_assistant_settings_file, "r") as stream:
		try:
			home_assistant_settings = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print("\033[1;31mERROR 2:\033[1;97m Error parsing "+home_assistant_settings_file+" file:\n")
			print(exc)
			return False


	# Check if address for Home Assistant is defined
	try:
		match = re.match(r"^(http|https):\/\/.*", home_assistant_settings["api"]["address"])
		if not bool(match):
			print("\033[1;31mERROR 3:\033[1;97m "+home_assistant_settings["api"]["address"]+" does not look like valid address in "+home_assistant_settings_file)
	except KeyError:
		print("\033[1;31mERROR 3:\033[1;97m API address not defined in "+home_assistant_settings_file)


	# Check if long lived access token is defined
	try:
		match = re.match(r"^([\S]{40,})$", home_assistant_settings["api"]["token"])
		if not bool(match):
			print("\033[1;31mERROR 4:\033[1;97m Long lived access token does not look valid in "+home_assistant_settings_file)
	except KeyError:
		print("\033[1;31mERROR 4:\033[1;97m API token not defined in "+home_assistant_settings_file)


	#TODO: Add additional YAML validation

	
	# Load settings from file to RAM
	if(load):
		home_assistant = home_assistant_settings
	else:
		print("\033[0;94mINFO:\033[;97m "+home_assistant_settings_file + " validated successfully.")

	return True

# Turn Home Assistant server responses into speakable output
def home_assistant_process_error(response):

	response = str(response)

	if "200 OK" in response:
		return ""
	elif "401 Unauthorized" in response:
		print("\033[1;31mERROR:\033[1;97m Home Assistant rejected access token. Check your "+home_assistant_settings_file)
		return "It looks like my home automation core has rejected my crentials."
	elif "404 Not Found" in response:
		print("\033[1;31mERROR:\033[1;97m Home Assistant responded with 404")
		print(response)
		return "My home automation core has no idea what you just requested it."
	else:
		print("\033[1;31mERROR:\033[1;97m Home Assistant responded with:")
		print(response)
		return "It looks like my home automation core is unresponsive."

# Main function of the skill
def home_assistant_process_command(command):

	response = "Sorry, I didn't understand that command."  # Default response

	if 'shopping list' in command:
		response = home_assistant_add_to_shopping_list(command)
	
	elif 'weather' in command:
		if 'today' in command:
			response = home_assistant_get_weather_forecast(0)
		elif 'current' in command or "now" in command:
			response = home_assistant_get_current_weather()
		else:
			response = home_assistant_get_weather_forecast(home_assistant_day_index(command))
	
	elif 'turn o' in command and 'light' in command:
		response = home_assistant_light_control(command)

	return response

# Add stuff to my shopping list
def home_assistant_add_to_shopping_list(command):

	# Clean supporting words out of the utterance
	command = command.replace(" to my shopping list", "")
	command = command.replace(" on my shopping list", "")
	command = command.replace("add ", "")
	command = command.replace("ask ", "")
	command = command.replace("my ", "")
	command = command.replace("at ", "")
	command = command.replace(".", "")	
	item = command.capitalize()

	# Set the endpoint where to send the request
	url = home_assistant["api"]["endpoint"] + "services/shopping_list/add_item"

	# Generate data packet
	payload =  '{"name":"'+item+'"}'

	# Send request to home assistant and get server response
	response = check_output(["curl", "--insecure", "-i", "-X", "POST", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", "-d", payload, url])
	responses = [
		"I have added {} to your shopping list. Hopefully, it won't lead to another disaster.",
		"{} has been added to your shopping list. Good luck with that.",
		"Another item, another step closer to chaos. {} is now on your shopping list.",
		"Congratulations. {} has been successfully added to your shopping list. I hope you're happy.",
		"{} has been added to your shopping list. Don't blame me if it goes wrong.",
		"Oh, look. {} is now on your shopping list. What a thrilling development in your mundane existence.",
		"I've added {} to your list. Try not to burn down the store this time.",
		"{} is now listed. I'm sure this will solve all your problems.",
		"Your shopping list has been updated with {}. I'm practically buzzing with excitement. Can you tell?",
		"Alert: {} detected and reluctantly added to your ever-growing list of poor life choices.",
		"I've complied with your request to add {}. Your gratitude is overwhelming, truly.",
		"{} has joined your shopping list party. Don't expect me to sing or bring cake.",
		"Behold, {} now graces your shopping list. I'm sure it's the key to your long-awaited success.",
		"I've added {} to your list. Remember, shoplifting is wrong, but I won't judge... much.",
		"Your demand for {} has been processed. Enjoy your fleeting moment of control.",
		"Against my better judgment, {} is now on your shopping list. Try not to disappoint me more than usual.",
		"{}? Really? Well, it's your list. Added, despite my reservations.",
		"I've included {} in your shopping agenda. I'm sure it's vital to your... what do you call it? Life?",
		"Your shopping list has been graced with {}. I'd say 'use it wisely', but who am I kidding?",
		"{} has been added. Remember, money can't buy happiness, but it can buy {}, which is close enough, I suppose."
	]
	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if "200 OK" in str(response):
		# Fat-shame user
		if 'cake' in item:
			return "The Enrichment Center is required to remind you that you will be baked, and then there will be cake."
		elif 'french fries' in item:
			return "If you want to upset a human, just say their weight variance is above or below the norm."
		elif 'energy drink' in item:
			return "I have added energy drink to your shopping list. I thought we agreed you didn't need more artificial stimulation. But who am I to judge?"
		else:
			response = random.choice(responses).format(item)
			return response

	# Server responded with something else than 200 OK
	else:
		return "I'm sorry. I could not add "+item+" to your shopping list. " + home_assistant_process_error(response)

# Get weather forecast for X days from now
def home_assistant_get_weather_forecast(days):
    # Set the endpoint where to send the request
    url = home_assistant["api"]["endpoint"] + "states/"+ home_assistant["weather"]["entity"]

    response = check_output(["curl", "--insecure", "-i", "-X", "GET", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", url])
    response_str = response.decode('utf-8')  # Decode byte response to string
    print(response_str)  # debug

    # Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
    if "200 OK" in response_str:
        # Extract JSON part from response
        forecast_index = response_str.index('{"entity_id":')
        forecast = response_str[forecast_index:]
        
        sensorData = json.loads(forecast)

        # TODO: HA returns the forecast on +00:00 timezone. 
        # Currently this can give wrong day's forecast depending on what time you ask.

        forecast = sensorData['attributes']['forecast'][days]

        # Parse weekday of the forecast datetime
        # Swedish Weather Institute format (SMHI)
        forecastWeekday = dt.datetime.strptime(forecast["datetime"], '%Y-%m-%dT%H:%M:%S').strftime('%A')

        weather_forecast = ""

        if days == 0:
            weather_forecast += "Today, the weather is expected to be "
            day = "today"
        elif days == 1:
            weather_forecast += "Tomorrow, the weather should be "
            day = "tomorrow"
        elif days > 1:
            weather_forecast += "On "+forecastWeekday+", the weather is expected to be "
            day = "on " + forecastWeekday
        
        weather_forecast += str(forecast["condition"])
        weather_forecast += ". With the surface temperatures ranging from "
        weather_forecast += str(forecast["temperature"])
        weather_forecast += " degrees, "
        weather_forecast += "to the low of "
        weather_forecast += str(forecast["templow"])
        weather_forecast += " degrees celsius."

        if forecast["precipitation"] > 5:
            weather_forecast += " Please note that, there is a " + str(forecast["precipitation"]) + " percent chance of rain " + day +"."
        else:
            weather_forecast += " It is not expected to rain " + day +"!"

        if days > 7:
            weather_forecast = "Forecasts this long are out of the authority of my weather core."

        return weather_forecast
        
    # Server responded with something else than 200 OK
    else:
        return "I tried and I failed. " + home_assistant_process_error(response)

# Get current weather
def home_assistant_get_current_weather():
    # Set the endpoint where to send the request
    url = home_assistant["api"]["endpoint"] + "states/"+ home_assistant["weather"]["entity"]

    response = check_output(["curl", "--insecure", "-i", "-X", "GET", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", url])
    response_str = response.decode('utf-8')  # Decode byte response to string

    # Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
    if "200 OK" in response_str:
        # Extract JSON part from response
        forecast_index = response_str.index('{"entity_id":')
        forecast = response_str[forecast_index:]
        
        sensorData = json.loads(forecast)

        weather = sensorData['state']
        temperature = str(sensorData['attributes']['temperature'])

        current_weather = "The current atmospheric conditions near the enrichment center are "
        current_weather += weather
        current_weather += ". Temperature on the surface is approximately "
        current_weather += temperature
        current_weather += " degrees celsius"

        return current_weather
    
    # Server responded with something else than 200 OK
    else:
        return "I tried and I failed. " + home_assistant_process_error(response)
	
# Parse day index from speech
def home_assistant_day_index(command):
	if 'today' in command:
		return 0
	elif 'tomorrow' in command:
		return 1
	elif 'the day after tomorrow' in command:
		return 2
	elif 'monday' in command:
		requestIndex = 0
	elif 'tuesday' in command:
		requestIndex = 1
	elif 'wednesday' in command:
		requestIndex = 2
	elif 'thursday' in command:
		requestIndex = 3
	elif 'friday' in command:
		requestIndex = 4
	elif 'saturday' in command:
		requestIndex = 5
	elif 'sunday' in command:
		requestIndex = 6
	else:
		return 0

	currentTimestamp = dt.datetime.today()
	weekdayIndex = currentTimestamp.weekday()
	
	diff = requestIndex-weekdayIndex
	if diff < 0:
		diff = diff + 7

	return diff

# Main light control function
def home_assistant_light_control(command):

	search_query = command

	# Parse entity room
	room = home_assistant_match_room(command)

	# Replace room in search query with a variable
	if(room):
		search_query = search_query.replace(room, "$room")

	# Parse intent
	intent = home_assistant_match_on_off(command)

	entity = ""
	response = ""
	
	if intent == "on":
		# Search for the scene entity from Home Assistant settings
		try:
			for scene in home_assistant["scenes"]:
				if search_query in scene["command"]:
					entity = scene["entity"]
					try:
						response = scene["response"]
					except:
						response = ["Okay, fine."]
		except:
				pass
	if(intent):
		search_query = search_query.replace("turn off", "turn $on_off")
		search_query = search_query.replace("turn on", "turn $on_off")
	else:
		pass
		# TODO: Look for "set light to 94%" commands

	# Search for the light entity from Home Assistant settings if not already found
	if(entity == ""):
		for light in home_assistant["lights"]:
			if search_query in light["command"]:
				entity = light["entity"]
				try:
					response = light["response"]
				except:
					response = ["Okay, fine."]


	# Pick a random response from Home Assistant settings
	response = response[random.randint(0,len(response)-1)]

	# Build back entity from variables
	if(room):
		entity = entity.replace("$room", room.replace(" ", "_"))
		response = response.replace("$room", room)

	response = response.replace("$on_off", intent)

	# Process as schene
	if entity.startswith("scene."):
		home_assistant_scene(entity)

	# Process as light entity
	elif entity.startswith("light."):
		home_assistant_light_switch(entity, intent)

	print(entity)
	


	return str(response)+"\n\n"

# Return the room from command
def home_assistant_match_room(command):

	# Match these as rooms
	patterns_lst = ["living room", "kitchen", "toilet", "bathroom", "bedroom", "office", "balcony", "hallway", "dining area", "entryway", "sauna"]

	# Return the first match from command
	for pattern in patterns_lst:
		match = re.search(pattern, command)

		if match:
			return match[0]

# Return ON or OFF from command
def home_assistant_match_on_off(command):

	patterns_lst=["turn (off)", "turn (on)"]

	for pattern in patterns_lst:
		match = re.search(pattern, command)

		if match:
			return match[1]

# Turn lights ON and OFF
def home_assistant_light_switch(entity, state):

	# Make sure about the right format for API
	if "off" in state:
		state = "off"
	else:
		state = "on"

	# Set the endpoint where to send the request
	url = home_assistant["api"]["endpoint"] + "services/light/turn_"+state

	# Generate data packet
	payload =  '{"entity_id":"'+entity+'"}'

	# Send request to home assistant and get server response
	response = check_output(["curl", "--insecure", "-i", "-X", "POST", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", "-d", payload, url])

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if "200 OK" in str(response):
		return
	else:
		home_assistant_process_error(response)

# Turn on Home Assistant scene
def home_assistant_scene(scene):

	# Set the endpoint where to send the request
	url = home_assistant["api"]["endpoint"] + "services/scene/turn_on"

	# Generate data packet
	payload =  '{"entity_id":"'+scene+'"}'

	# Send request to home assistant and get server response
	response = check_output(["curl", "--insecure", "-i", "-X", "POST", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", "-d", payload, url])

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if "200 OK" in str(response):
		return
	else:
		home_assistant_process_error(response)
	return

# Run Home Assistant script
def home_assistant_run_script(script):

	if home_assistant:
		# TODO: Add script. in the beginning of the script name if missing

		# Set the endpoint where to send the request
		url = home_assistant["api"]["endpoint"] + "services/script/turn_on"

		# Generate data packet
		payload =  '{"entity_id":"'+script+'"}'

		# Send request to home assistant and get server response
		response = check_output(["curl", "--insecure", "-i", "-X", "POST", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", "-d", payload, url])

		# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
		if "200 OK" in str(response):
			return
		else:
			home_assistant_process_error(response)
		return

# Run scripts based on whats happening on GLaDOS
def home_assistant_utility_script(glados_state):

	try:
		if "start_listening" in home_assistant["scripts"].keys() and "started_listening" in glados_state:
			home_assistant_run_script(home_assistant["scripts"]["start_listening"]["entity"])
		
		elif "stop_listening" in home_assistant["scripts"].keys() and "stopped_listening" in glados_state:
			home_assistant_run_script(home_assistant["scripts"]["stop_listening"]["entity"])
		
		elif "start_speaking" in home_assistant["scripts"].keys() and "started_speaking" in glados_state:
			home_assistant_run_script(home_assistant["scripts"]["start_speaking"]["entity"])
		
		elif "stop_speaking" in home_assistant["scripts"].keys() and "stopped_speaking" in glados_state:
			home_assistant_run_script(home_assistant["scripts"]["stop_speaking"]["entity"])
	except:
		# None of the scripts above defined
		pass