# GLaDOS Voice Assistant
DIY Voice Assistant based on the GLaDOS character from Portal video game series.

* Designed for Raspberry Pi
* Written mostly in Python
* Work in progress

## Description
### 📺 [GLaDOS Voice Assistant | Introduction](https://www.youtube.com/embed/Y3h5tKWqf-w)
### 📺 [GLaDOS Voice Assistant | Software - Python tutorial](https://youtu.be/70_imR6cBGc)
### 🛠 [Check out the GLaDOS Voice Assistant project on Twitter](https://twitter.com/search?q=(%23glados)%20(from%3Anerdaxic)&src=typed_query)

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

## To use:
You can add glados.py to your crontab file or run it manually.
``` 
crontab -e
@reboot python3 /home/username/GLaDOS-Voice-Assistant/glados.py
``` 
Additionally you can configure the ReSpeaker at startup by adding following lines to root's crontab:
``` 
sudo su
crontab -e
@reboot bash /home/username/GLaDOS-Voice-Assistant/hardware/ReSpeaker/ReSpeaker_Startup_Config.sh
@reboot python3 /home/username/GLaDOS-Voice-Assistant/hardware/ReSpeaker/ReSpeaker_Turn_off_Pixelring.py
``` 

## Hardware
List of reference hardware what [nerdaxic](https://github.com/nerdaxic/) is developing on, models might not need to be exact. 
Not a full bill of materials.
| Item | Description |
| ---- | ----------- |
| Main board | [Raspberry Pi 4 Model B 8GB](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) |
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
