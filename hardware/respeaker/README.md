# ReSpeaker configuration
Copy 50-respeaker.rules to /etc/udev/rules.d and reboot to allow python script to access to ReSpeaker hardware.
```console
sudo cp ~/glados-voice-assistant/hardware/respeaker/50-respeaker.rules /etc/udev/rules.d
sudo reboot now
```
Install pixel-ring library
```console
sudo pip3 install pixel-ring
```
Test. This should turn the blue lights off.
```console
python3 -c "from pixel_ring import pixel_ring; pixel_ring.off()"
```