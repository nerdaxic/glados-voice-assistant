sudo apt update
sudo apt upgrade
sudo apt install git
sudo apt install python3-pip
sudo apt install portaudio19-dev
sudo apt-get install -y build-essential swig libpulse-dev libasound2-dev
sudo apt-get install flac
git clone --recurse-submodules https://github.com/nerdaxic/glados-voice-assistant/
cd ~/glados-voice-assistant
sudo pip3 install -r requirements.txt
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
sudo pip3 install -r requirements.txt
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
cd ~/glados-voice-assistant/glados_tts/
python3 glados.py
