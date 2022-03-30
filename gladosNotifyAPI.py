from flask import Flask, request
from gladosTTS import *

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/notify")
def notify():
    message = request.args.get('message')

    print("\nNOTIFY API: " + message + "\n")

    try:
    	speak(message.lower())
    except Exception as e:
    	raise
    
    return "Notify API"

# TODO: Add endpoint for volume level control.
# amixer -D pulse sset Master 50%

if __name__ == "__main__":
	app.run(host="0.0.0.0")