#!/bin/bash
# This runs at startup with root crontab to setup the mic array parameters.
# Run at startup with root crontab
echo "Resetting Mic Array..."
# Set gain to automatic and about 26 dB
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py AGCONOFF 0
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py AGCGAIN 20
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py AGCDESIREDLEVEL 0.08
# Turn off most audio processing
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py ECHOONOFF 0
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py NLATTENONOFF 0
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py NLAEC_MODE 0
# Settings when speech is detected
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py STATNOISEONOFF 0
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py NONSTATNOISEONOFF 0
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py GAMMA_NS 1
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py GAMMA_NN 1
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py MIN_NN 1
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py MIN_NS 1
# When speech treshold is not crossed
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py STATNOISEONOFF_SR 1
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py NONSTATNOISEONOFF_SR 1
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py GAMMA_NS_SR 1.5
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py GAMMA_NN_SR 1.5
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py MIN_NN_SR 0.0
#python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py MIN_NS_SR 0.0
# Speech recognition level
python3 /home/nerdaxic/respeakerDFU/usb_4_mic_array/tuning.py GAMMAVAD_SR 3
# Check if ran correctly
#touch /home/nerdaxic/GLaDOS/mic.sh