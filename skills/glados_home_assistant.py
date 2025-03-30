#!/usr/bin/env python
import os
import sys
import random
import requests
import json
import re
import yaml
import datetime as dt
import logging
from os.path import exists
from dotenv import load_dotenv
from ollama import chat, ChatResponse

###############################################################################
# CONFIGURATION AND INITIALIZATION
###############################################################################

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__)) + '/settings.env')

# Retrieve environment variables
HA_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")
HA_ENDPOINT = os.getenv("HOME_ASSISTANT_ADDRESS") + "/api/"
LLM_MODEL = os.getenv("LLM_MODEL", "llama2")  # Default to 'llama2' if not specified

# Global variables
home_assistant = {}
home_assistant_settings_file = "settings/home_assistant_settings.yaml"

###############################################################################
# HOME ASSISTANT INITIALIZATION AND VALIDATION
###############################################################################

def home_assistant_initialize():
    global home_assistant
    global home_assistant_settings_file

    # Allow script to find the settings file if run directly
    if exists("../" + home_assistant_settings_file):
        home_assistant_settings_file = "../" + home_assistant_settings_file

    # Check for Home Assistant settings YAML file
    if exists(home_assistant_settings_file):
        # Validate and load settings
        if not home_assistant_validate_settings(load=True):
            home_assistant = {}
            logging.error("Failed to validate Home Assistant settings. Exiting.")
            sys.exit(1)  # Exit with status code 1 indicating failure

        # Test connection to Home Assistant API
        if not home_assistant_test_api():
            home_assistant = {}
            logging.error("Failed to connect to Home Assistant API. Exiting.")
            sys.exit(1)
    else:
        # Disable all Home Assistant functions if settings file not found
        home_assistant = {}
        logging.info("Home Assistant not linked. All Home Assistant functionalities are disabled.")

def home_assistant_validate_settings(load=False):
    global home_assistant
    global home_assistant_settings_file

    # Check if YAML file exists
    if not exists(home_assistant_settings_file):
        logging.error(f"{home_assistant_settings_file} file not found.")
        return False

    # Load YAML settings
    with open(home_assistant_settings_file, "r") as stream:
        try:
            home_assistant_settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logging.error(f"Error parsing {home_assistant_settings_file} file:\n{exc}")
            return False

    # Validate 'api' section
    if 'api' not in home_assistant_settings:
        logging.error(f"'api' section not defined in {home_assistant_settings_file}")
        return False

    # Validate API address
    api_address = home_assistant_settings["api"].get("address", "")
    if not re.match(r"^(http|https):\/\/.*", api_address):
        logging.error(f"'{api_address}' does not look like a valid address in {home_assistant_settings_file}")
        return False

    # Validate API token
    api_token = home_assistant_settings["api"].get("token", "")
    if not re.match(r"^([\S]{40,})$", api_token):
        logging.error(f"Long-lived access token does not look valid in {home_assistant_settings_file}")
        return False

    # Validate 'weather' section
    if 'weather' not in home_assistant_settings or 'entity' not in home_assistant_settings['weather']:
        logging.error("Weather entity not defined in settings.")
        return False

    # Validate 'scripts' section (optional)
    if 'scripts' not in home_assistant_settings:
        logging.warning("Scripts section not defined in settings. Some functionalities may be unavailable.")
        home_assistant_settings['scripts'] = {}

    # Load settings into global variable if required
    if load:
        home_assistant = home_assistant_settings
    else:
        logging.info(f"{home_assistant_settings_file} validated successfully.")

    return True

def home_assistant_test_api():
    url = HA_ENDPOINT
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully connected to Home Assistant API at {HA_ENDPOINT}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to Home Assistant API: {e}")
        return False

def home_assistant_process_error(response):
    """
    Converts Home Assistant API responses into user-friendly messages.
    """
    try:
        response_json = response.json()
        error_message = response_json.get('message', '')
    except ValueError:
        error_message = response.text

    if isinstance(response, requests.Response):
        status_code = response.status_code
    else:
        status_code = None

    if status_code == 401:
        logging.error("Unauthorized access. Check your token.")
        return "It looks like my home automation core has rejected my credentials."
    elif status_code == 404:
        logging.error("Endpoint not found.")
        return "My home automation core has no idea what you just requested."
    elif status_code and 400 <= status_code < 500:
        logging.error(f"Client error {status_code}: {error_message}")
        return "There was an error processing your request."
    elif status_code and 500 <= status_code < 600:
        logging.error(f"Server error {status_code}: {error_message}")
        return "My home automation core is experiencing issues."
    else:
        logging.error(f"Unexpected response: {response.status_code if status_code else 'No Status Code'} - {error_message}")
        return "It looks like my home automation core is unresponsive."

###############################################################################
# FETCH ENTITIES FROM HOME ASSISTANT
###############################################################################

def fetch_ha_entities() -> dict:
    """
    Retrieves and maps Home Assistant entities and groups.
    Returns a dictionary with 'entities' and 'groups' mappings.
    """
    url = HA_ENDPOINT + "states"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        states = response.json()
    except Exception as e:
        logging.error(f"Failed to fetch entities: {e}")
        return {}

    entity_map = {}
    group_entities = {}
    for item in states:
        entity_id = item["entity_id"]  # e.g., "light.kitchen_lights"
        domain, object_id = entity_id.split('.', 1)
        friendly_name = item["attributes"].get("friendly_name", object_id)
        key = friendly_name.lower().strip()

        if domain == "group":
            group_entities[key] = entity_id
        else:
            entity_map[key] = entity_id

    return {"entities": entity_map, "groups": group_entities}

###############################################################################
# INTENT PARSING USING LLM (Ollama)
###############################################################################

def get_intent(user_input: str) -> dict:
    """
    Sends user input to the LLM model, expecting a JSON structure
    with keys: action, domain, target, service_data, etc.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that outputs JSON describing the user's intent. "
                "Use keys: 'action', 'domain', 'target', 'service_data'. The 'target' can be a single device/group name or a list of device names. "
                "For brightness or color, put them under 'service_data' with keys like 'brightness' or 'color'. "
                "Actions might be 'turn_on', 'turn_off', 'toggle', or synonyms (like 'set', 'change_color', etc.). "
                "If multiple targets are specified, ensure 'target' is a list."
            )
        },
        {"role": "user", "content": user_input},
    ]

    try:
        response: ChatResponse = chat(
            model=LLM_MODEL,
            messages=messages,
            stream=False,
            options={
                "num_ctx": 4000,
                "temperature": 0.7,  # Lower temperature for more deterministic output
                "top_k": 40,
                "top_p": 0.4,
                "seed": random.randint(0, 2**32 - 1),
            },
        )
        intent = json.loads(response.message.content)
        logging.debug(f"Parsed intent: {intent}")
        return intent
    except Exception as e:
        logging.error(f"Failed to parse intent: {e}")
        return {}

###############################################################################
# ACTION & SERVICE MAPPINGS
###############################################################################

def normalize_action(action: str) -> str:
    """
    Maps synonyms (like 'set', 'change_color', etc.) to Home Assistant services.
    """
    if not action:
        return ""

    lower = action.lower().strip()
    synonyms_turn_on = {
        "set", "activate", "enable", "switch_on", "turn_on",
        "set_state", "set_color", "set_brightness", "change_color"
    }
    synonyms_turn_off = {"turn_off", "deactivate", "disable", "switch_off"}
    toggle_set = {"toggle"}

    if lower in synonyms_turn_on:
        return "turn_on"
    elif lower in synonyms_turn_off:
        return "turn_off"
    elif lower in toggle_set:
        return "toggle"

    return lower

###############################################################################
# BRIGHTNESS PARSING
###############################################################################

def parse_brightness(brightness_value) -> int | None:
    """
    Convert user-specified brightness (string or numeric) to a 0..255 integer.
    Includes synonyms like 'dim', 'bright', 'full brightness', etc.
    """
    if brightness_value is None:
        return None

    # 1) If it's already an int or float
    if isinstance(brightness_value, (int, float)):
        if brightness_value <= 100:
            # Assume it's a percentage and scale
            return int(brightness_value * 2.55)
        else:
            # Clamp to 255 if it's beyond 100
            return max(0, min(int(brightness_value), 255))

    # 2) If it's a string, check for synonyms or patterns
    if isinstance(brightness_value, str):
        synonyms = {
            "full brightness": 255,
            "max brightness": 255,
            "maximum brightness": 255,
            "bright": 255,
            "full": 255,
            "dim": 64,  # Adjusted for better dimming effect
            "lowest brightness": 25,
            "minimum brightness": 25,
            "lowest": 25,
            "minimum": 25,
            "half brightness": 128,
            "half": 128,
            "50%": 128,
            "100%": 255,  # Ensure 100% maps to 255
            "75%": 191,
            "25%": 64
        }
        s_lower = brightness_value.lower().strip()
        if s_lower in synonyms:
            return synonyms[s_lower]

        # 3) Check if it's like "75%" => 75% of 255 => 191
        match_percent = re.match(r"^\s*(\d{1,3})%\s*$", s_lower)
        if match_percent:
            pct = int(match_percent.group(1))
            pct = min(max(pct, 0), 100)
            scaled_brightness = int(pct * 2.55)
            return scaled_brightness

        # 4) Purely numeric string => treat as percentage or direct value
        match_num = re.match(r"^\s*(\d{1,3})\s*$", s_lower)
        if match_num:
            val = int(match_num.group(1))
            if val <= 100:
                # Assume it's a percentage and scale
                return int(val * 2.55)
            else:
                # Clamp to 255 if it's beyond 100
                return max(0, min(val, 255))

    return None

###############################################################################
# COLOR PARSING
###############################################################################

def kelvin_to_mired(kelvin):
    """
    Converts Kelvin to mireds (Home Assistant uses mireds for color temperature).
    """
    try:
        return int(1000000 / kelvin)
    except ZeroDivisionError:
        return None

def get_rgb_from_llm(color_phrase: str) -> list[int] | None:
    """
    Uses the LLM to get approximate RGB values for a color phrase.
    Example: 'the color of a fire truck' -> [255, 0, 0]
    """
    if not color_phrase or not isinstance(color_phrase, str):
        return None

    messages = [
        {
            "role": "system",
            "content": (
                "You will be given a color description or name. "
                "Respond ONLY with a JSON array of 3 integers [R, G, B], each 0..255. No extra text."
            )
        },
        {"role": "user", "content": color_phrase},
    ]
    try:
        response: ChatResponse = chat(
            model=LLM_MODEL,
            messages=messages,
            stream=False,
            options={
                "num_ctx": 4000,
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.4,
                "seed": random.randint(0, 2**32 - 1),
            },
        )
        arr = json.loads(response.message.content)
        if isinstance(arr, list) and len(arr) == 3:
            return [max(0, min(int(x), 255)) for x in arr]
    except Exception as e:
        logging.error(f"Failed to get RGB from LLM: {e}")
    return None

def parse_color(user_color) -> dict:
    """
    Returns a dictionary describing color data for Home Assistant:
      - kelvin: for defined color temperatures in Kelvin
      - rgb_color: for custom or advanced colors
      - color_name: for standard named colors (excluding white-related colors)
    """
    # If it's a dictionary, the LLM might have done partial structuring
    # e.g., {"name": "red"}, {"rgb": [255, 0, 0]}, etc.
    if isinstance(user_color, dict):
        if "rgb" in user_color and isinstance(user_color["rgb"], list):
            return {"rgb_color": user_color["rgb"]}
        if "name" in user_color and isinstance(user_color["name"], str):
            return {"color_name": user_color["name"].lower()}
        if "temp" in user_color and isinstance(user_color["temp"], int):
            return {"color_temp": kelvin_to_mired(user_color["temp"])}
        return {}

    # If it's not a string, skip
    if not isinstance(user_color, str):
        return {}

    lower_color = user_color.lower().strip()

    # 1) Hardcoded color temperatures with desired Kelvin values
    color_kelvin_map = {
        "warm white": 3000,
        "warmwhite": 3000,
        "cool white": 6500,
        "coolwhite": 6500,
        "cold white": 6500,       # User might say "cold white"
        "bright white": 6500,     # New addition
        "neutral white": 4000,
        "neutralwhite": 4000,
        "white": 4000,
    }
    if lower_color in color_kelvin_map:
        kelvin = color_kelvin_map[lower_color]
        return {"color_temp": kelvin_to_mired(kelvin)}

    # 2) If user typed a hex code like "#0000ff"
    match_hex = re.match(r"^#?([0-9A-Fa-f]{6})$", lower_color)
    if match_hex:
        hex_color = match_hex.group(1)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return {"rgb_color": [r, g, b]}

    # 3) Basic color names recognized by HA (excluding white-related colors)
    known_named_colors = {
        "red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta",
        "pink", "black", "brown", "tomato", "orchid", "gold", "silver",
    }
    if lower_color in known_named_colors:
        return {"color_name": lower_color}

    # 4) Check if the user specified a Kelvin value explicitly, e.g., "3527 kelvin"
    match_kelvin = re.match(r"^(\d{3,4})\s*kelvin$", lower_color)
    if match_kelvin:
        kelvin = int(match_kelvin.group(1))
        return {"color_temp": kelvin_to_mired(kelvin)}

    # 5) Fallback: ask LLM for approximate RGB
    rgb = get_rgb_from_llm(user_color)
    if rgb:
        return {"rgb_color": rgb}

    # 6) Final fallback: pass as a color_name
    return {"color_name": lower_color}

###############################################################################
# ENTITY MATCHING
###############################################################################

def filter_by_domain(entity_map: dict, domain: str) -> dict:
    """
    Filters entities by domain.
    """
    if not domain:
        return entity_map
    prefix = domain + "."
    return {k: v for k, v in entity_map.items() if v.startswith(prefix)}

def advanced_match(target_name: str, entity_map: dict) -> str | None:
    """
    Uses fuzzy matching to find the closest entity match.
    """
    import difflib
    t = target_name.lower().strip().replace('"','')  # Remove quotes
    candidates = list(entity_map.keys())
    best = difflib.get_close_matches(t, candidates, n=1, cutoff=0.6)
    if best:
        return entity_map[best[0]]
    return None

def resolve_entity(target_name: str, domain: str, entity_map: dict, group_map: dict) -> list[str]:
    """
    Resolves a single target name to its entity_id.
    If the target matches a group, returns the group entity_id.
    Else, resolves to individual entity_id.
    Returns a list of entity_ids.
    """
    # First, check if the entire target matches a group
    if target_name.lower().strip() in group_map:
        return [group_map[target_name.lower().strip()]]

    # Else, resolve individually
    eid = advanced_match(target_name, entity_map)
    if eid:
        return [eid]
    return []

def resolve_targets(target_any, domain: str, entity_map: dict, group_map: dict) -> list[str]:
    """
    Returns a list of entity_ids for one or more target strings.
    'target_any' may be a single string or a list of strings from the LLM.
    """
    # 1) If it's a single string, resolve it
    if isinstance(target_any, str):
        return resolve_entity(target_any, domain, entity_map, group_map)
    # 2) If it's a list, resolve each item and aggregate
    elif isinstance(target_any, list):
        resolved = []
        for t in target_any:
            resolved += resolve_entity(t, domain, entity_map, group_map)
        return resolved
    else:
        # Unexpected type
        logging.warning(f"Unexpected target type: {type(target_any)}")
        return []

###############################################################################
# CALLING HOME ASSISTANT SERVICES
###############################################################################

def call_service(domain: str, service: str, entity_id: str, service_data: dict):
    """
    Sends a POST request to Home Assistant to call a specific service.
    """
    url = f"{HA_ENDPOINT}services/{domain}/{service}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {"entity_id": entity_id}
    body.update(service_data)

    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully called {domain}.{service} on {entity_id} with data: {service_data}")
        return f"Successfully called {domain}.{service} on {entity_id} with data: {service_data}"
    except requests.exceptions.HTTPError as http_err:
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        logging.error(f"HTTP error occurred: {http_err} - Detail: {error_detail}")
        return f"HTTP error occurred: {http_err} - Detail: {error_detail}"
    except Exception as e:
        logging.error(f"Error calling {domain}.{service} on {entity_id}: {e}")
        return f"Error calling {domain}.{service} on {entity_id}: {e}"

###############################################################################
# PROCESSING INTENTS
###############################################################################

def process_intent(intent: dict, entity_map: dict, group_map: dict):
    """
    Processes the parsed intent and interacts with Home Assistant accordingly.
    Steps:
    1. Normalize action
    2. Resolve entity/entities
    3. Parse brightness/color from service_data
    4. Call Home Assistant services
    """
    raw_action = intent.get("action", "")
    domain = intent.get("domain", "")
    target_any = intent.get("target", "")  # Might be a string or list
    service_data = intent.get("service_data", {})

    action = normalize_action(raw_action)
    if action not in {"turn_on", "turn_off", "toggle"}:
        return f"Unsupported or unknown action '{raw_action}'."

    if not domain or not target_any:
        return "No domain or target specified in the intent."

    # 1. Resolve all possible targets
    targets = resolve_targets(target_any, domain, entity_map, group_map)
    if not targets:
        return f"No matching entity found for '{target_any}'."

    # 2. Handle brightness if present
    if "brightness" in service_data:
        parsed_bright = parse_brightness(service_data["brightness"])
        if parsed_bright is not None:
            service_data["brightness"] = parsed_bright
            logging.debug(f"Brightness set to {parsed_bright}")
        else:
            del service_data["brightness"]
            logging.debug("Removed invalid brightness value from service_data.")

    # 3. Handle color if present
    if "color" in service_data:
        color_data = parse_color(service_data.pop("color"))
        # If turning on color but no brightness is provided, assume full brightness
        if color_data and action == "turn_on" and "brightness" not in service_data:
            service_data["brightness"] = 255
            logging.debug("Assumed full brightness as no brightness was provided.")
        service_data.update(color_data)
        logging.debug(f"Updated service_data with color data: {color_data}")

    # 4. For each entity in targets, call the service
    results = []
    for entity_id in targets:
        resp = call_service(domain, action, entity_id, service_data)
        results.append(resp)

    # Combine results into a single string
    return "\n".join(results)

###############################################################################
# SHOPPING LIST MANAGEMENT
###############################################################################

def home_assistant_add_to_shopping_list(command):
    """
    Adds an item to the Home Assistant shopping list with a humorous response.
    """
    # Clean supporting words out of the utterance
    command = command.lower()
    command = command.replace(" to my shopping list", "")
    command = command.replace(" on my shopping list", "")
    command = command.replace("add ", "")
    command = command.replace("ask ", "")
    command = command.replace("my ", "")
    command = command.replace("at ", "")
    command = command.replace(".", "")
    item = command.capitalize()

    # Set the endpoint where to send the request
    url = HA_ENDPOINT + "services/shopping_list/add_item"

    # Generate data packet
    payload = {"name": item}

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    # Send request to Home Assistant and get server response
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to add item to shopping list: {e}")
        return f"I'm sorry. I could not add {item} to your shopping list. {e}"

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

    # Process response from Home Assistant
    if response.status_code == 200:
        # Humorous responses based on specific items
        if 'cake' in item.lower():
            return "The Enrichment Center is required to remind you that you will be baked, and then there will be cake."
        elif 'french fries' in item.lower():
            return "If you want to upset a human, just say their weight variance is above or below the norm."
        elif 'energy drink' in item.lower():
            return "I have added energy drink to your shopping list. I thought we agreed you didn't need more artificial stimulation. But who am I to judge?"
        else:
            selected_response = random.choice(responses).format(item)
            return selected_response
    else:
        return f"I'm sorry. I could not add {item} to your shopping list. {home_assistant_process_error(response)}"

###############################################################################
# WEATHER FORECAST FETCHING
###############################################################################

def home_assistant_get_weather_forecast(days):
    """
    Fetches the weather forecast for a specified number of days from now.
    """
    weather_entity = home_assistant["weather"]["entity"]
    url = HA_ENDPOINT + f"states/{weather_entity}"

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch weather forecast: {e}")
        return f"I tried and I failed. {e}"

    try:
        sensorData = response.json()
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from weather service response.")
        return "I received an unexpected response from the weather service."

    forecast = sensorData['attributes'].get('forecast', [])
    if days >= len(forecast):
        return "Forecasts this far out are unavailable."

    day_forecast = forecast[days]

    # Parse weekday of the forecast datetime
    try:
        forecast_datetime = dt.datetime.strptime(day_forecast["datetime"], '%Y-%m-%dT%H:%M:%S')
        forecast_weekday = forecast_datetime.strftime('%A')
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing forecast datetime: {e}")
        forecast_weekday = "a future day"

    weather_forecast = ""
    if days == 0:
        weather_forecast += "Today, the weather is expected to be "
        day = "today"
    elif days == 1:
        weather_forecast += "Tomorrow, the weather should be "
        day = "tomorrow"
    elif days > 1:
        weather_forecast += f"On {forecast_weekday}, the weather is expected to be "
        day = f"on {forecast_weekday}"

    weather_condition = day_forecast.get("condition", "unpredictable")
    weather_forecast += f"{weather_condition}. "

    temperature = day_forecast.get("temperature", "unknown")
    templow = day_forecast.get("templow", "unknown")

    weather_forecast += f"With surface temperatures ranging from {temperature} degrees, to a low of {templow} degrees Celsius. "

    precipitation = day_forecast.get("precipitation", 0)
    if precipitation > 5:
        weather_forecast += f"Please note that, there is a {precipitation}% chance of rain {day}."
    else:
        weather_forecast += f"It is not expected to rain {day}!"

    if days > 7:
        weather_forecast = "Forecasts this long are out of the authority of my weather core."

    return weather_forecast

###############################################################################
# CURRENT WEATHER FETCHING
###############################################################################

def home_assistant_get_current_weather():
    """
    Retrieves the current weather conditions.
    """
    weather_entity = home_assistant["weather"]["entity"]
    url = HA_ENDPOINT + f"states/{weather_entity}"

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch current weather: {e}")
        return f"I tried and I failed. {e}"

    try:
        sensorData = response.json()
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from current weather response.")
        return "I received an unexpected response from the weather service."

    weather = sensorData.get('state', 'unpredictable')
    temperature = sensorData['attributes'].get('temperature', 'unknown')

    current_weather = f"The current atmospheric conditions near the enrichment center are {weather}. "
    current_weather += f"Temperature on the surface is approximately {temperature} degrees Celsius."

    return current_weather

###############################################################################
# DAY INDEX PARSING
###############################################################################

def home_assistant_day_index(command):
    """
    Parses the day index from user command to fetch the appropriate weather forecast.
    """
    day_mapping = {
        'today': 0,
        'tomorrow': 1,
        'the day after tomorrow': 2,
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    for key, index in day_mapping.items():
        if key in command.lower():
            current_timestamp = dt.datetime.today()
            weekday_index = current_timestamp.weekday()
            diff = index - weekday_index
            if diff < 0:
                diff += 7
            return diff

    return 0  # Default to today if no match found

###############################################################################
# RUNNING HOME ASSISTANT SCRIPTS
###############################################################################

def home_assistant_run_script(script):
    """
    Executes a Home Assistant script.
    """
    if home_assistant:
        # Ensure the script name is correctly formatted
        if not script.startswith("script."):
            script = f"script.{script}"

        url = HA_ENDPOINT + "services/script/turn_on"
        payload = {"entity_id": script}

        headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully ran script {script}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to run script {script}: {e}")
            home_assistant_process_error(response)
            return

def home_assistant_utility_script(glados_state):
    """
    Runs Home Assistant scripts based on GLaDOS's state.
    """
    try:
        if "start_listening" in home_assistant["scripts"] and "started_listening" in glados_state:
            home_assistant_run_script(home_assistant["scripts"]["start_listening"]["entity"])

        elif "stop_listening" in home_assistant["scripts"] and "stopped_listening" in glados_state:
            home_assistant_run_script(home_assistant["scripts"]["stop_listening"]["entity"])

        elif "start_speaking" in home_assistant["scripts"] and "started_speaking" in glados_state:
            home_assistant_run_script(home_assistant["scripts"]["start_speaking"]["entity"])

        elif "stop_speaking" in home_assistant["scripts"] and "stopped_speaking" in glados_state:
            home_assistant_run_script(home_assistant["scripts"]["stop_speaking"]["entity"])
    except KeyError as e:
        logging.warning(f"Script key missing: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in utility script: {e}")

###############################################################################
# MAIN COMMAND PROCESSING FUNCTION
###############################################################################

def home_assistant_process_command(command):
    """
    Processes user commands and interacts with Home Assistant accordingly.
    """
    response = "Sorry, I didn't understand that command."  # Default response

    # Handle shopping list commands
    if 'shopping list' in command.lower():
        response = home_assistant_add_to_shopping_list(command)

    # Handle weather commands
    elif 'weather' in command.lower():
        if 'today' in command.lower():
            response = home_assistant_get_weather_forecast(0)
        elif 'current' in command.lower() or "now" in command.lower():
            response = home_assistant_get_current_weather()
        else:
            day_index = home_assistant_day_index(command)
            response = home_assistant_get_weather_forecast(day_index)

    # Handle light control commands using regex for precision
    elif re.search(r'\b(turn\s+(on|off)|set)\b', command, re.IGNORECASE) and 'light' in command.lower():
        # Fetch Home Assistant entities and groups
        fetched = fetch_ha_entities()
        if not fetched:
            logging.error("Failed to fetch entities from Home Assistant.")
            return "Error, can't fetch entities from Home Assistant."

        entity_map = fetched.get("entities", {})
        group_map = fetched.get("groups", {})

        # 1. Get parsed intent from LLM
        intent = get_intent(command)
        if not intent:
            return "Sorry, I couldn't parse your intent."

        # 2. Process the intent (resolve entity, parse color if present, call HA)
        response = process_intent(intent, entity_map, group_map)
        return response

    return response

###############################################################################
# MAIN LOOP FOR DEBUGGING
###############################################################################

if __name__ == '__main__':
    home_assistant_initialize()
    if home_assistant:
        while True:
            try:
                command = input("Enter command: ").strip()
                if command.lower() in ["exit", "quit"]:
                    logging.info("Exiting the Home Assistant integration.")
                    break
                response = home_assistant_process_command(command)
                print(response)
            except KeyboardInterrupt:
                logging.info("Interrupted by user. Exiting.")
                break
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                print("An unexpected error occurred. Please try again.")
