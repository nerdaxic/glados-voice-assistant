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
	print(response.text)

	# Check if cheese.wav exists and respond
	if 'Cake' in item:
		speak("The Enrichment Center is required to remind you that you will be baked, and then there will be cake.")
	elif 'French fries' in item:
		speak("If you want to upset a human, just say their weight variance is above or below the norm.")

	else:
		# Item audio not found, random generic OK response
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
	
	elif "g/m³" in sensorUnit:
		sensorValue = round(sensorValue,1)
		
	else:
		sensorValue = int(sensorValue)

	# Check if value.wav is available, if not, get it before to speak full sentences.
	if not checkTTSLib(str(sensorValue)):
		# Play "hold on"
		#playFile('audio/GLaDOS-wait-'+str(randint(1, 2))+'.wav')
		fetchTTSSample(str(sensorValue))

	if not checkTTSLib("The "+cleanTTSLine(sensorName)):
		fetchTTSSample("The "+cleanTTSLine(sensorName))

	speak("The "+sensorName)
	speak("is currently")
	speak(str(sensorValue))
	speak(sensorUnit)

	return sensorValue

def saySaunaCompleteTime(temperature):
	readyTemp = 60
	minutesLeft = int(8/3*(readyTemp-int(temperature)))
	print(minutesLeft)
	readyTime = dt.datetime.today() + dt.timedelta(minutes = minutesLeft)
	print(readyTime)
	hour = readyTime.strftime('%H')
	minute = readyTime.strftime('%M')

	speak("The operational temperature will be reached approximately at")
	speak(hour)
	playFile('audio/clock/minute/GLaDOS-'+minute+'.wav')

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
	
	#playFile('audio/GLaDOS-kerava-weather.wav')
	speak("The current atmospheric conditions near the enrichment center are")
	speak(weather)
	speak("Temperature on the surface is approximately")
	speak(temperature)
	speak("°C")

# 0 being today, 1 tomorrow, etc
def sayforecastfromHA(days):
	url = endpoint+"states/"+os.getenv('HOME_ASSISTANT_WEATHER_ENTITY')
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	#print(url)
	try:
		response = requests.get(url, headers=headers, verify=False)
	except:
		return False
		pass
	
	sensorData = json.loads(response.text)
	
	print("Days: "+str(days))
	forecast = sensorData['attributes']['forecast'][days]

	print("forecast: "+str(forecast))

	# Parse weekday of the forecast datetime
	forecastWeekday = dt.datetime.strptime(forecast["datetime"], '%Y-%m-%dT%H:%M:%S').strftime('%A')

	if(days == 0):
		speak("Today, it's expected to be")
	if(days == 1):
		speak("Tomorrow, the weather should be")
	if(days > 1):
		speak("On "+forecastWeekday+" the weather is expected to be ")
	if(days > 7):
		speak("Forecasts this long are out of the authority of my weather core")

	speak(str(forecast["condition"]))
	speak("with the surface temperatures ranging from")
	speak(str(forecast["temperature"]))
	speak("°")
	speak("to the low of")
	speak(str(forecast["templow"]))
	speak("°C")

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

	print("requestIndex :"+str(requestIndex ))
	print("weekdayIndex:"+str(weekdayIndex))

	
	diff = requestIndex-weekdayIndex
	if diff < 0:
		diff = diff + 7


	print("diff: "+str(diff))

	return diff

def call_HA_Service(service, entity, data=""):

	domain = service.partition(".")[0]
	service = service.partition(".")[2]

	url = endpoint+"services/"+domain+"/"+service
	
	print(url)
	headers = {
	 "Authorization": "Bearer "+token,
	 "content-type": "application/json",
	}

	if data != "":
		data = ", "+data

	payload = '{"entity_id": "'+entity+'"'+data+'}'

	response = requests.post(url, headers=headers, data=payload, verify=False)
	print(response.content)