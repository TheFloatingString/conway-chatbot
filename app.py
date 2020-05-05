import os
import requests
import random
from flask import Flask, request, render_template

def create_emotions_dict(sheet_id, sheet_api_key):

	sheet_url = "https://sheets.googleapis.com/v4/spreadsheets/"+sheet_id+"/values/A:D?key="+sheet_api_key+"&majorDimension=columns"
	response = requests.get(sheet_url).json()
	emotions_dict = dict()

	for emotion_list in response["values"]:
		emotions_dict[emotion_list[0]] = emotion_list[1:]

	return emotions_dict

def get_wit(user_input, auth_key):

	encoded_input = requests.utils.quote(user_input, safe='')

	headers =  {"Authorization": "Bearer "+os.getenv("AUTH_KEY")}
	wit_url = "https://api.wit.ai/message?v=20200421&n=8&q="+encoded_input

	response = requests.get(wit_url, headers=headers)

	return response

# get responses
emotions_dict = create_emotions_dict(sheet_id=os.getenv("SHEET_ID"), sheet_api_key=os.getenv("SHEET_API_KEY"))


app = Flask(__name__)

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/ask", methods=["GET"])
def ask():
	user_input = request.args.get("q")
	print(user_input)
	wit_resp = get_wit(user_input, os.getenv("AUTH_KEY")).json()
	return_resp = "Undefined"

	print(wit_resp['entities'])

	# define goodbye
	if wit_resp["entities"].get("bye") is not None and wit_resp["entities"]["bye"][0]["confidence"] > 0.7:
		return_resp = "Goodbye!"

	elif wit_resp["entities"].get("greetings") is not None and wit_resp["entities"]["greetings"][0]["confidence"] > 0.7:
		return_resp = "Hello there!"
			
	# define emotion response
	elif wit_resp["entities"].get("intent") is not None and wit_resp["entities"]["intent"][0]["confidence"] > 0.7:
		intent = wit_resp["entities"]["intent"][0]["value"]
		return_resp = random.choice(emotions_dict[intent])
	
	else:
		return_resp = random.choice(emotions_dict["not_recognized"])

	return return_resp

if __name__ == '__main__':
	app.run(debug=True)