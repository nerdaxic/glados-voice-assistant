#!/usr/bin/python3
import os
import yaml

glados_settings_file = "settings/glados_settings.yaml"
settings = ""

def load_from_file():
	# Load settings to variables from setting file
	global glados_settings_file
	global settings

		# Allow script to find the settings file if ran directly
	if (os.path.exists("../"+glados_settings_file)):
		glados_settings_file = "../"+glados_settings_file

	# Check for setting YAML
	if (os.path.exists(glados_settings_file)):

		# Check if YAML is valid and load it to RAM
		with open(glados_settings_file, "r") as stream:
			try:
				settings = yaml.safe_load(stream)
				return settings
			except yaml.YAMLError as exc:
				print("\033[1;31mERROR:\033[1;97m Error parsing "+glados_settings_file+" file:\n")
				print(exc)
				exit()

	else:
		settings = False
		print(glados_settings_file + " file not found.")
		exit()