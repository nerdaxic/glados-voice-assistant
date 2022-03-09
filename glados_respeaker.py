#!/usr/bin/python3
try:
	from pixel_ring import pixel_ring
except Exception as e:		
	print(e)
def respeaker_pixel_ring(rgb=0x200000):

	# Set respeaker to dim glow inside the head.
	# See hardware folder for more info.
	try:
		pixel_ring.off()
		pixel_ring.set_color(rgb)
	except Exception as e:
		print(e)


def respeaker_mode(mode):
	if(mode == "listen"):
		try:
			pixel_ring.listen()
		except Exception as e:
			print(e)
	elif(mode == "wait"):
		try:
			pixel_ring.wait() 
		except Exception as e:
			print(e)