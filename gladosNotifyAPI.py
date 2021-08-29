#flask run --host=0.0.0.0

from flask import Flask, request
from gladosTTS import *

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/notify")
def notify():
    message = request.args.get('message')
    try:
    	speak(message.lower())
    except Exception as e:
    	raise
    
    return "Notify API"

if __name__ == "__main__":
	app.run(host="0.0.0.0")