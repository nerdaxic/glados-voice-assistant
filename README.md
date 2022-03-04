# GLaDOS Voice Assistant
DIY Voice Assistant based on the GLaDOS character from Portal video game series.
## Featured on:
🛠 [Hackday](https://www.tomshardware.com/news/raspberry-pi-glados-voice-assistant-head) - Tech blog

🛠 [Tom's Hardware](https://www.tomshardware.com/news/raspberry-pi-glados-voice-assistant-head) - Technology news

🎮 [PCGamer](https://www.pcgamer.com/this-guy-decided-to-mock-our-future-ai-overlords-with-a-glados-smart-assistant/) - Online magazine

🇫🇮 [Ilta-Sanomat](https://www.is.fi/digitoday/art-2000008642371.html) - The second largest newspaper in Finland

🇫🇮 [Muropaketti](https://muropaketti.com/tietotekniikka/tietotekniikkauutiset/onpas-hieno-suomalainen-youtube-kayttaja-teki-portal-pelin-glados-tekoalyrobotista-huiman-hienon-aaniavustajan/) - Finnish computing website

## Read project article first!
📄 [GLaDOS Voice Assistant](https://www.henrirantanen.fi/2022/02/10/glados-voice-assistant-with-custom-text-to-speech/?utm_source=github.com&utm_medium=social&utm_campaign=post&utm_content=DIY+GLaDOS+Voice+Assistant+with+Python+and+Raspberry+Pi) - henrirantanen.fi

## Description
* Written mostly in Python
* Work in progress

❗ New versions of the voice assistant will not work on Raspberry Pi due to missing CPU instruction sets needed by some AI scripts. If you are looking to play along with the old version on your Raspberry Pi, check the [raspberry branch](https://github.com/nerdaxic/glados-voice-assistant/tree/raspberry).

* YouTube 📺 [GLaDOS Voice Assistant | Introduction](https://www.youtube.com/embed/Y3h5tKWqf-w)
* YouTube 📺 [GLaDOS Voice Assistant | Software - Python tutorial](https://youtu.be/70_imR6cBGc)
* Twitter 🛠 [GLaDOS Voice Assistant project build](https://twitter.com/search?q=(%23glados)%20(from%3Anerdaxic)&src=typed_query)

## Main features
1. Local Trigger word detection using PocketSphinx
2. Local GLaDOS Text-to-Speech engine using [glados-tts model by R2D2FISH](https://github.com/nerdaxic/glados-tts)
3. Speech-to-text processing using Google's API (for now)
4. Local TTS cache of generated common audio samples locally for instant answers in the future
5. Animatronic eye control using servos
6. Round LCD for an eye to display display textures

Tight integration with Home Assistant's local API:
* Send commands to Home Assistant
* Read and speak sensor data
* Notification API, so Home Assistant can speak out notifications through GLaDOS

## What it can do:
* Clock
* Control lights and devices
* Weather and forecast
* Add things to shopping list
* Read sensor information
* Random magic 8-ball answers
* Tell jokes
* Judge you and be mean
* Advanced fat-shaming
* Log stuff and gather training data locally


> Note: The code is provided as reference only.
## Voice Assistant pipeline overview
![General AI Voice Assistant Pipeline](https://www.henrirantanen.fi/wp-content/uploads/2022/02/ai-voice-assistant-pipeline.jpg)


## Requirements
### Install PyAudio
PyAudio is needed to play audio files.
```console 
sudo apt-get update 
sudo apt-get upgrade 
sudo apt-get install portaudio19-dev 
sudo pip3 install pyaudio
``` 
### Install python-dotenv
Used to parse the settings file.
```console 
sudo pip3 install python-dotenv
``` 
### Install PocketSphinx
Used for trigger word detection for now.
```console 
sudo apt-get install -y build-essential swig libpulse-dev libasound2-dev
sudo pip3 install pocketsphinx
``` 

### Install SpeechRecognition 
Used to turn audio into text for now.
```console 
sudo pip3 install SpeechRecognition
sudo apt-get install flac
``` 
### Install sounddevice 
Used for selecting sound cards
```console 
sudo pip3 install sounddevice
``` 
### Install other libraries
Should be already installed on Raspberry
```console 
sudo pip3 install pyserial
sudo pip3 install psutil
sudo pip3 install flask
sudo snap install curl
``` 


## Install GLaDOS Voice Assistant

#### 1. Go to home folder
```console 
cd ~
``` 
#### 2. Download the source from GitHub
```console 
git clone https://github.com/nerdaxic/glados-voice-assistant/
``` 
#### 3. Edit the settings file

Find the sound card ID:
```console
python3 -m sounddevice
```
Generate and edit the settings.env file:
```console 
cp glados-voice-assistant/settings.env.sample glados-voice-assistant/settings.env && nano glados-voice-assistant/settings.env
``` 
#### 4. To run:
Launch the voice assistant:
```console
python3 ~/glados-voice-assistant/glados.py
```

You can add glados.py to your crontab file or run it manually.
```console
crontab -e
@reboot python3 /home/username/glados-voice-assistant/glados.py
```

## Integrate to Home Assistant

To make Home Assistant integration work, you need to enable the API in the home assistant configuration file and generate a long-lived access token.
Add access token and IP-address of the home assistant server into the settings.env file.
### configuration.yaml

```YAML 
# This will enable rest api
api:

# This will add GLaDOS as a notification provider. Replace with correct IP of GLaDOS.
notify:
  - name: glados
    platform: rest
    resource: http://192.168.1.XXX:5000/notify
``` 

## Hardware
List of reference hardware what [nerdaxic](https://github.com/nerdaxic/) is developing on, models might not need to be exact. 
Not a full bill of materials.
| Item | Description |
| ---- | ----------- |
| Main board | Basic i7 laptop with 16 gigs of RAM|
| Operating system | ubuntu-20.04.3-desktop-amd64 |
| Microcontroller | [Teensy 4](https://www.pjrc.com/store/teensy40.html), to control the eye LCD and NeoPixels |
| Eye lights | [Adafruit NeoPixel Diffused 5mm Through-Hole](https://www.adafruit.com/product/1938) for the "REC" light |
| Eye lights  | [Adafruit 16 x 5050 NeoPixel Ring](https://www.adafruit.com/product/1463) |
| Eye LCD | [1.28 Inch TFT LCD Display Module Round, GC9A01 Driver SPI Interface 240 x 240](https://www.amazon.de/gp/product/B08G8MVCCZ/) |
### Audio
Audio amp is powered from Raspberry GPIO 5V line and ReSpeaker board from USB to avoid ground loops and noise issues.
| Item | Description |
| ---- | ----------- |
| Audio amplifier | [Adafruit Stereo 3.7W Class D Audio Amplifier](https://www.adafruit.com/product/987) |
| Speakers | [Visaton FRS 7](https://www.amazon.de/gp/product/B0056BQAFC/) |
| Microphone & Audio interface | [ReSpeaker Mic Array V2.0](https://www.seeedstudio.com/ReSpeaker-Mic-Array-v2-0.html) |
### Mechanics
Mechanics are powered from their own power supply to allow more power for the servos and prevent brown-outs.
| Item | Description |
| ---- | ----------- |
| Power supply | [MeanWell LRS-50-5 5V](https://www.amazon.de/gp/product/B00MWQDH00/) |
| Servo controller | [Pololu Micro Maestro](https://www.pololu.com/product/1350/) |
| Servo: Eye movement | [35 kg DS3235 (Control Angle 180)](https://www.amazon.de/gp/product/B07T725ZV5/) |
| Servo: Eyelids | [25 kg DS3225 (Control Angle 180)](https://www.amazon.de/gp/product/B08BZNSLQF/) |
| Screws | [Various M3 and M4 screws](https://www.amazon.de/gp/product/B073SS7D8J/) |
| Jumper wires | [0.32 mm²/22 AWG assortment](https://www.amazon.de/gp/product/B07TV5VXZ2/) |
