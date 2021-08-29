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
* Rapsberry PI 4
* Memory card
* Respeaker Mic Array V2.0
