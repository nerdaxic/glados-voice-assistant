# GLaDOS Voice Assistant
DIY Voice Assistant based on the GLaDOS character from Portal video game series.

* Designed for Raspberry Pi 4 Model B (8 GB) V 1.4
* Written mostly in Python
* Work in progress

This branch is made so that the software runs on Raspberry Pi. Future versions will need neural network related functions not found in current ARM instruction set and thus can not run on Raspberry Pi.

## Read article first!
[DIY GLaDOS Voice Assistant with Python and Raspberry Pi](https://www.henrirantanen.fi/2022/02/10/diy-glados-raspberry-pi-voice-assistant/?utm_source=github.com&utm_medium=social&utm_campaign=post&utm_content=DIY+GLaDOS+Voice+Assistant+with+Python+and+Raspberry+Pi)

## Description
* YouTube 📺 [GLaDOS Voice Assistant | Introduction](https://www.youtube.com/embed/Y3h5tKWqf-w)
* YouTube 📺 [GLaDOS Voice Assistant | Software - Python tutorial](https://youtu.be/70_imR6cBGc)
* Twitter 🛠 [GLaDOS Voice Assistant project build](https://twitter.com/search?q=(%23glados)%20(from%3Anerdaxic)&src=typed_query)

## Main features
1. Local Trigger word detection using PocketSphinx
2. Speech to text processing using Google's API (for now)
3. GLaDOS Text-to-Speech generation using https://glados.c-net.org/
4. Storing of generated audio samples locally for instant answers in the future
5. Animatronic eye control using servos
5. Round LCD for an eye to display display textures

Tight integration with Home Assistant's local API:
* Send commands to Home Assistant
* Can read and speak sensor data
* Notification API, so Home Assistant can speak notifications aloud

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

## Set up Raspberry Pi
### 1) Install 64-bit Raspberry Pi operating system
Use [Win32DiskImager](https://sourceforge.net/projects/win32diskimager/) or [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to write the operating system to a microSD card.

📀 [2022-01-28-raspios-bullseye-arm64.zip](https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2022-01-28/2022-01-28-raspios-bullseye-arm64.zip)

### 2) Once finished writing the image to SD-card, go the the drive labelled "boot" and add following files:
#### 📄 Add wpa_supplicant.conf
This file gives Raspberry Pi your wifi details so you can automatically connect to your wifi so you can log in with SSH without plugging in keyboard etc.
Add your wifi network name, password and [ISO/IEC alpha2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) in which the device is operating.
``` ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
     ssid="Your wifi network name here"
     psk="Wifi password here"
     scan_ssid=1
}
``` 

#### 📄 Add empty file called "ssh" without file extension
This tells the operating system to enable SSH so you can log in remotely.

[Full guide here](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-headless-raspberry-pi)

### 3) Start up the Raspberry Pi
1. Umnount SD-card
2. Insert card into Raspberry Pi
3. Plug in the power
4. Device should connect to your WIFI automatically

### 4) Login to Raspberry Pi
You can use the client list in your router to find the IP-address of the Raspberry Pi.
While you in there, I would recommend to set the DHCP server to always give the Raspberry Pi the same IP, or later setting a static IP in the Raspberry Pi config.

You can use [Putty](https://www.puttygen.com/download-putty) or Linux command line to log into Paspberry PI

| Item | Value |
| :---- | -----------: |
| Address | Check your router |
| Default port | 22 |
| Username | Pi |
| Default password | raspberry |
| Protocol | SSH |

### 5) Secure your Raspberry Pi
The server can have access keys & login tokens to your accounts & systems, so take your time to secure your server.

[Securing your Raspberry Pi](https://www.raspberrypi.com/documentation/computers/configuration.html#securing-your-raspberry-pi)

## Requirements
### Install PyAudio
PyAudio is needed to play audio files.
``` 
sudo apt-get update 
sudo apt-get upgrade 
sudo apt-get install portaudio19-dev 
sudo pip3 install pyaudio
``` 
### Install python-dotenv
Used to parse the settings file.
``` 
sudo pip3 install python-dotenv
``` 
### Install PocketSphinx
Used for trigger word detection for now.
``` 
sudo apt-get install -y build-essential swig libpulse-dev libasound2-dev
sudo pip3 install pocketsphinx
``` 

### Install SpeechRecognition 
Used to turn audio into text for now.
``` 
sudo pip3 install SpeechRecognition
sudo apt-get install flac
``` 
### Install sounddevice 
Used for selecting sound cards
``` 
sudo pip3 install sounddevice
``` 
### Install other libraries
Should be already installed on Raspberry
``` 
sudo pip3 install serial
sudo pip3 install psutil
``` 


## Install GLaDOS Voice Assistant on your Raspberry Pi

1. Go to home folder
``` 
cd ~
``` 
2. Download the source from GitHub
``` 
git clone https://github.com/nerdaxic/glados-voice-assistant/
``` 
3. Edit the settings file
Find the sound card ID with:
```
python3 -m sounddevice
```
Write settings to file:
``` 
cp glados-voice-assistant/settings.env.sample glados-voice-assistant/settings.env && nano glados-voice-assistant/settings.env
``` 
4. To run:

Launch the voice assistant:
```
python3 ~/glados-voice-assistant/glados.py
```

You can add glados.py to your crontab file or run it manually.
``` 
crontab -e
@reboot python3 /home/username/glados-voice-assistant/glados.py
``` 
Additionally you can configure the ReSpeaker at startup by adding following lines to root's crontab:
``` 
sudo su
crontab -e
@reboot bash /home/username/glados-voice-assistant/hardware/ReSpeaker/ReSpeaker_Startup_Config.sh
@reboot python3 /home/username/glados-voice-assistant/hardware/ReSpeaker/ReSpeaker_Turn_off_Pixelring.py
``` 

## Hardware
List of reference hardware what [nerdaxic](https://github.com/nerdaxic/) is developing on, models might not need to be exact. 
Not a full bill of materials.
| Item | Description |
| ---- | ----------- |
| Main board | [Raspberry Pi 4 Model B 8GB V1.4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) |
| Power supply for Digital + Audio | [Raspberry Pi 15W USB-C Power supply](https://www.raspberrypi.org/products/type-c-power-supply/) |
| Memory card | Class 10 64 GB microSDXC U3 |
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
