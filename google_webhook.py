import picamera
import requests
import time
from flask import Flask
from flask_assistant import Assistant, ask, tell

app = Flask(__name__)
assist = Assistant(app)

KERAS_REST_API_OBJECT = "http://192.168.0.6:5000/predict"
IMAGE_PATH_OBJECT = "google_object.jpg"

KERAS_REST_API_FACE = "http://192.168.0.6:5000/predictface"
IMAGE_PATH_FACE = "google_face.jpg"



@app.route('/',methods=['GET','POST'])
def index():
	return "hello! I'm a google image classifier"

@assist.action('greetings')
def greet_and_start():
	msgText = "Hi, would you like to take a photo of an object or a face?"
	return ask(msgText)


@assist.action("face")
def id_face():
	camera = picamera.PiCamera()
	camera.capture(IMAGE_PATH_FACE)
	time.sleep(.5)
	camera.close()
	image = open(IMAGE_PATH_FACE, "rb").read()
	payload = {"image": image}


	r = requests.post(KERAS_REST_API_FACE, files=payload).json()
	tensor_text = ""
	if r["success"]:
		for (i, result) in enumerate(r["predictions"]):
			tensor_text = result["label"]
			tensor_text = tensor_text.replace("_", " ")
			tensor_text = tensor_text.replace("b'","")
			break
	else:
		tensor_text = "Whoops!, Something broke"


	msgText = "I think this person is " + tensor_text
	print(msgText)
	return tell(msgText)

@assist.action("object")
def id_obejct():
	#msgText = "its the object intent"

	camera = picamera.PiCamera()
	camera.capture(IMAGE_PATH_OBJECT)
	time.sleep(.5)
	camera.close()
	image = open(IMAGE_PATH_OBJECT, "rb").read()
	payload = {"image": image}


	r = requests.post(KERAS_REST_API_OBJECT, files=payload).json()
	tensor_text = ""
	if r["success"]:
		for (i, result) in enumerate(r["predictions"]):
			tensor_text = result["label"]
			tensor_text = tensor_text.replace("_", " ")
			break
	else:
		tensor_text = "Whoops!, Something broke"


	msgText = "I think its a " + tensor_text
	print(msgText)
	
	return tell(msgText)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)