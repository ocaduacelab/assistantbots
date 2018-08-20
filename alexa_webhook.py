#!/usr/bin/python

import logging
import picamera
import requests
import time

from flask import Flask
from flask_ask import Ask, statement, question, session, statement, request


app = Flask(__name__)
ask = Ask(app, "/")

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


KERAS_REST_API_URL_OBJECT = "http://192.168.0.6:5000/predict"
KERAS_REST_API_URL_FACE = "http://192.168.0.6:5000/predictface"

IMAGE_PATH_OBJECT = "alexa_object.jpg"
IMAGE_PATH_FACE = "alexa_face.jpg"



@app.route('/',methods=['GET','POST'])
def index():
	return "hello!"

@ask.on_session_started
def new_session():
	log.info('new session started')
	log.info(request.locale)
	beep = request.locale
	print(beep)

@ask.launch
def launch():
	msgText = "Hi, would you like to take a photo of an object or a face?"
	return question(msgText)


@ask.intent("face")
def see_face():
	camera = picamera.PiCamera()
	camera.capture(IMAGE_PATH_FACE)
	time.sleep(.5) # Give it a tad to write the file.  If it
				   # fails to write and you get a blank image
				   # tensor flow will report it as a website 
	camera.close()
	image = open(IMAGE_PATH_FACE, "rb").read()
	payload = {"image": image}

	r = requests.post(KERAS_REST_API_URL_FACE, files=payload).json()
	tensor_text = ""
	if r["success"]:
		for (i, result) in enumerate(r["predictions"]):
			tensor_text = result["label"]
			tensor_text = tensor_text.replace("_", " ")
			break
	else:
		tensor_text = "Whoops!, Something broke"


	msgText = "I think this person is " + tensor_text
	return statement(msgText)



@ask.intent("object")
def see_object():
	camera = picamera.PiCamera()
	camera.capture(IMAGE_PATH_OBJECT)
	time.sleep(.5) # Give it a tad to write the file.  If it
				   # fails to write and you get a blank image
				   # tensor flow will report it as a website 
	camera.close()
	image = open(IMAGE_PATH_OBJECT, "rb").read()
	payload = {"image": image}

	r = requests.post(KERAS_REST_API_URL_OBJECT, files=payload).json()
	tensor_text = ""
	if r["success"]:
		for (i, result) in enumerate(r["predictions"]):
			tensor_text = result["label"]
			tensor_text = tensor_text.replace("_", " ")
			break
	else:
		tensor_text = "Whoops!, Something broke"


	msgText = "I think it's a " + tensor_text
	return statement(msgText)


@ask.intent('AMAZON.HelpIntent')
def help():
	speech_text = "Looking at things!"
	return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)


@ask.session_ended
def session_ended():
	return "{}", 200


if __name__ == '__main__':
	app.config['ASK_VERIFY_REQUESTS'] = False
	app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)