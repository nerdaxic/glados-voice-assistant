#!/usr/bin/python3
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.dirname(os.path.abspath(__file__))+'/settings.env')


# Parse error messages into most common help hints
def respeaker_errors(e):
	if "Access denied" in str(e):
		print("\nERROR: No permission to access ReSpeaker hardware.")
		print("Check the README.md for udev rules in the hardware/respeaker folder.")
		exit();
	if "No such device" in str(e):
		print("\nERROR: ReSpeaker is not connected.")
		exit();
	if "No such file of directory" in str(e):
		print("\nERROR: Library missing.")
		print("Run 'sudo pip3 install pixel_ring'")
		exit();
	if "name 'pixel_ring' is not defined" in str(e) and os.getenv('RESPEAKER_CONNECTED'):
		print("\nERROR: ReSpeaker is probably not connected?")
		exit();
	else:
		print(e)

# Try to load the ReSpeaker pixel ring library
if(os.getenv('RESPEAKER_CONNECTED')):
	try:
		from pixel_ring import pixel_ring
	except Exception as e:
		respeaker_errors(e)

# Set the ring to static color.
# Input 8 bit HEX color codes
def respeaker_pixel_ring(rgb=0x100000):

	# Set respeaker to dim glow inside the head.
	# See hardware folder for more info.
	if(os.getenv('RESPEAKER_CONNECTED')):
		try:
			pixel_ring.set_color(rgb)
		except Exception as e:
			respeaker_errors(e)

# Set respeaker to animation modes
def respeaker_mode(mode):
	if(os.getenv('RESPEAKER_CONNECTED')):
		if(mode == "listen"):
			try:
				pixel_ring.listen()
			except Exception as e:
				respeaker_errors(e)
		elif(mode == "wait"):
			try:
				pixel_ring.wait() 
			except Exception as e:
				respeaker_errors(e);
