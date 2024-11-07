import requests
import os
from gladosTTS import *
import random
import json
import datetime as dt

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')

# Get settings form environment file
token = os.getenv('HOME_ASSISTANT_TOKEN')
endpoint = os.getenv('HOME_ASSISTANT_ADDRESS')+"/api/"

def addToShoppingList(item):

	item = item.replace(" to my shopping list", "")
	item = item.replace(" on my shopping list", "")
	item = item.replace("add ", "")
	item = item.replace("ask ", "")	
	item = item.capitalize()

	url = endpoint+"services/shopping_list/add_item"

	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	payload =  '{"name":"'+item+'"}'
	response = requests.post(url, headers=headers, data=payload, verify=False)

	if 'Cake' in item:
		speak("The Enrichment Center is required to remind you that you will be baked, and then there will be cake.")
	elif 'French fries' in item:
		speak("If you want to upset a human, just say their weight variance is above or below the norm.")
	else:
		speak("I have added "+item+" to your shopping list")

def activateScene(scene):
	url = endpoint+"services/scene/turn_on"
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	payload =  '{"entity_id":"'+scene+'"}'

	response = requests.post(url, headers=headers, data=payload, verify=False)

def runHaScript(script):
	url = endpoint+"services/script/"+script
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	response = requests.post(url, headers=headers, verify=False)

def lightSwitch(light, state="on"):
	url = endpoint+"services/light/turn_"+state
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	payload =  '{"entity_id":"'+light+'"}'

	response = requests.post(url, headers=headers, data=payload, verify=False)

def setCoverTo(position):
	url = endpoint+"services/script/"
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	if position == "closed":
		url +=  "close_bedroom_blinds"
	else:
		url += "1583532017564"

	response = requests.post(url, headers=headers, verify=False)

def sayNumericSensorData(sensor):

	delayMessage = [
		"Hold on",
		"Hang on, I need to check that.",
		"Give me a moment.",
		"Not that I care, but it'll take a second.",
		"Please wait while I pretend to check.",
		"Please stand by.",
		"Give me a moment to process this."
	]
	speak(random.choice(delayMessage), cache=True)

	url = endpoint+"states/"+sensor
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	try:
		response = requests.get(url, headers=headers, verify=False)
	except:
		return False
		pass
	sensorData = json.loads(response.text)
	sensorValue = float(sensorData['state']);	
	sensorName = sensorData['attributes']["friendly_name"]
	sensorUnit = sensorData['attributes']["unit_of_measurement"]

	if "°C" in sensorUnit:
		sensorValue = round(sensorValue,1)
		sensorUnit = "degrees celcius"
	
	elif "g/m³" in sensorUnit:
		sensorValue = round(sensorValue,1)
		sensorUnit = "grams per cubic meter"
		
	else:
		sensorValue = int(sensorValue)

	speak(cleanTTSLine("The " + sensorName + " is currently " + str(sensorValue)+" "+sensorUnit))
	

	return sensorValue

def saySaunaCompleteTime(temperature):
	readyTemp = 60
	minutesLeft = int(8/3*(readyTemp-int(temperature)))
	readyTime = dt.datetime.today() + dt.timedelta(minutes = minutesLeft)
	hour = readyTime.strftime('%H')
	minute = readyTime.strftime('%M')

	speak("The operational temperature will be reached approximately at "+hour+":"+minute)


def sayCurrentWeatherfromHA():
	url = endpoint+"states/"+os.getenv('HOME_ASSISTANT_WEATHER_ENTITY')
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	try:
		response = requests.get(url, headers=headers, verify=False)
	except:
		return False
		pass
		
	sensorData = json.loads(response.text)
	weather = sensorData['state'];
	temperature = str(sensorData['attributes']['temperature']);
	
	speak("The current atmospheric conditions near the enrichment center are")
	speak(weather)
	speak("Temperature on the surface is approximately")
	speak(temperature)
	speak("degrees celcius")

# 0 being today, 1 tomorrow, etc
def sayforecastfromHA(days):

	# Apologize for TTS delay
	speak("Let me check that for you, give me a moment.", cache=True)

	url = endpoint+"states/"+os.getenv('HOME_ASSISTANT_WEATHER_ENTITY')
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	try:
		response = requests.get(url, headers=headers, verify=False)
	except:
		return False
		pass
	
	sensorData = json.loads(response.text)

	# TODO: HA returns the forecast on +00:00 timezone. 
	# Currently this can give wrong day's forecast depending on what time you ask.

	forecast = sensorData['attributes']['forecast'][days]

	# Parse weekday of the forecast datetime
	# Swedish Weather Institute format (SMHI)
	forecastWeekday = dt.datetime.strptime(forecast["datetime"], '%Y-%m-%dT%H:%M:%S').strftime('%A')

	weather = ""

	if(days == 0):
		weather += "Today it's expected to be "
		day = "today"
	elif(days == 1):
		weather += "Tomorrow, the weather should be "
		day = "tomorrow"
	elif(days > 1):
		weather += "On "+forecastWeekday+" the weather is expected to be "
		day = "on " + forecastWeekday
	
	weather += str(forecast["condition"])
	weather += ", with the surface temperatures ranging from "
	weather += str(forecast["temperature"])
	weather += " degrees, "
	weather += "to the low of "
	weather += str(forecast["templow"])
	weather += " degrees celcius."

	speak(weather, cache=False)

	if(forecast["precipitation"] > 5):
		weather = " Please note that, there is a " + str(forecast["precipitation"]) + " procent chance of rain " + day +"."
	else:
		weather = " It is not expected to rain " + day +"."

	speak(weather, cache=False)

	if(days > 7):
		weather = "Forecasts this long are out of the authority of my weather core"
		speak(weather, cache=False)

def getDayIndex(command):
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

def call_HA_Service(service, entity, data=""):
    domain = service.partition(".")[0]
    service = service.partition(".")[2]

    url = endpoint + "services/" + domain + "/" + service
    
    headers = {
        "Authorization": "Bearer " + token,
        "content-type": "application/json",
    }

    if data != "":
        data = ", " + data

    payload = '{"entity_id": "' + entity + '"' + data + '}'

    response = requests.post(url, headers=headers, data=payload, verify=False)
    
    # Process response from Home Assistant, error handling if HA responds with something else than HTTP 200 OK
    if response.status_code == 200:
        return True, "Service call successful."
    else:
        error_message = f"Home Assistant responded with: {response.status_code} - {response.text}"
        return False, error_message
