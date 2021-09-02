# GLaDOS Voice Assistant
DIY Voice Assistant based on the GLaDOS character from Portal video game series.

[Check out the GLaDOS Voice Assistant project on Twitter](https://twitter.com/search?q=(%23glados)%20(from%3Anerdaxic)&src=typed_query)

## Main features
1. Trigger word detection running locally using PocketSphinx
2. Process speech to text using Google's API (for now)
3. GLaDOS Text-to-Speech generation with https://glados.c-net.org/
4. Store generated audio samples locally for instant answers in the future

Tight integration with Home Assistant's local API:
* Send commands to Home Assistant
* Can read and speak sensor data
* Notification API, so Home Assistant can speak notifications aloud

> Note: The code is provided as reference only.

## Hardware
* Rapsberry Pi 4
* Memory card
* ReSpeaker Mic Array V2.0
* Adafruit Stereo 3.7W Class D Audio Amplifier
* Raspberry Pi 15W USB-C Power supply for computer and audio
* MeanWell LRS-50-5 5V Power supply for power mechanics
* Pololu Micro Maestro 6-Channel USB Servo Controller

