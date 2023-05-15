import sys
import os
sys.path.insert(0, os.getcwd()+'/glados_tts')

import torch
from utils.tools import prepare_text
from scipy.io.wavfile import write
import time
		
print("\033[1;94mINFO:\033[;97m Initializing TTS Engine...")

# Select the device
if torch.is_vulkan_available():
	device = 'vulkan'
if torch.cuda.is_available():
	device = 'cuda'
else:
	device = 'cpu'

# Load models
if __name__ == "__main__":
	glados = torch.jit.load('models/glados.pt')
	vocoder = torch.jit.load('models/vocoder-gpu.pt', map_location=device)
else:
	glados = torch.jit.load('glados_tts/models/glados.pt')
	vocoder = torch.jit.load('glados_tts/models/vocoder-gpu.pt', map_location=device)

# Prepare models in RAM
for i in range(4):
	init = glados.generate_jit(prepare_text(str(i)))
	init_mel = init['mel_post'].to(device)
	init_vo = vocoder(init_mel)


def glados_tts(text, key=False):

	# Tokenize, clean and phonemize input text
	x = prepare_text(text).to('cpu')

	with torch.no_grad():

		# Generate generic TTS-output
		old_time = time.time()
		tts_output = glados.generate_jit(x)

		# Use HiFiGAN as vocoder to make output sound like GLaDOS
		mel = tts_output['mel_post'].to(device)
		audio = vocoder(mel)
		print("\033[1;94mINFO:\033[;97m The audio sample took " + str(round((time.time() - old_time) * 1000)) + " ms to generate.")

		# Normalize audio to fit in wav-file
		audio = audio.squeeze()
		audio = audio * 32768.0
		audio = audio.cpu().numpy().astype('int16')
		if(key):
			output_file = ('audio/GLaDOS-tts-temp-output-'+key+'.wav')
		else:
			output_file = ('audio/GLaDOS-tts-temp-output.wav')

		# Write audio file to disk
		# 22,05 kHz sample rate 
		write(output_file, 22050, audio)

	return True


# If the script is run directly, assume remote engine
if __name__ == "__main__":
	
	# Remote Engine Veritables
	PORT = 8124
	CACHE = True

	from flask import Flask, request, send_file
	import urllib.parse
	import shutil
	
	print("\033[1;94mINFO:\033[;97m Initializing TTS Server...")
	
	app = Flask(__name__)

	@app.route('/synthesize/', defaults={'text': ''})
	@app.route('/synthesize/<path:text>')
	def synthesize(text):
		if(text == ''): return 'No input'
		
		line = urllib.parse.unquote(request.url[request.url.find('synthesize/')+11:])
		filename = "GLaDOS-tts-"+line.replace(" ", "-")
		filename = filename.replace("!", "")
		filename = filename.replace("°c", "degrees celcius")
		filename = filename.replace(",", "")+".wav"
		file = os.getcwd()+'/audio/'+filename
		
		# Check for Local Cache
		if(os.path.isfile(file)):
		
			# Update access time. This will allow for routine cleanups
			os.utime(file, None)
			print("\033[1;94mINFO:\033[;97m The audio sample sent from cache.")
			return send_file(file)
			
		# Generate New Sample
		key = str(time.time())[7:]
		if(glados_tts(line, key)):
			tempfile = os.getcwd()+'/audio/GLaDOS-tts-temp-output-'+key+'.wav'
						
			# If the line isn't too long, store in cache
			if(len(line) < 200 and CACHE):
				shutil.move(tempfile, file)
			else:
				return send_file(tempfile)
				os.remove(tempfile)
				
			return send_file(file)
				
		else:
			return 'TTS Engine Failed'
			
	cli = sys.modules['flask.cli']
	cli.show_server_banner = lambda *x: None
	app.run(host="0.0.0.0", port=PORT)