import json
import os

import logging
import requests
import sys

formatter = '[%(asctime)-15s] %(levelname)s [%(filename)s.%(funcName)s#L%(lineno)d] - %(message)s'

logging.basicConfig(level = logging.DEBUG, format = formatter)

# Create logger instance
logger = logging.getLogger('api')
quiz_path = os.path.abspath("agoa.json")
resp_path = os.path.abspath("responses.json")

assets = {
	"quick": {
		"usage" : ["introduction"],
		"type" : "quick_replies"
	},
	"message" : {
		"type": "text"
	}
}

headers = {
	'Content-Type' : 'application/json'
}

graph = "https://graph.facebook.com/v3.2/me/messages?access_token={}"
__all__ = ['make_response', 'import_questions', 'find_user', 'make_quiz_response', 'check_answers']

_CURRENT_MODULE_ = sys.modules[__name__]

def get_response():
	responses = {}
	print(resp_path)
	try:
		with open(resp_path, "r") as store:
			responses = json.load(store)
			store.close()
	except (IOError, OSError):
		return responses
	return responses

def make_response(_id, t, k, token, **kwargs):
	loaded = None
	message = None

	response = get_response()
	if response:
		loaded = response.get(k, None)
	else:
		return None
	if not loaded:
		logger.error("Could not find specified option in provided responses.")
		return None

	handler_name = 'make_{}_replies'.format(t)
	req = 'send_{}_replies'.format(t)
	_type = assets[t]["type"]
	try:
		handler = getattr(_CURRENT_MODULE_, handler_name)
		message = handler(loaded)
		api_request = getattr(_CURRENT_MODULE_, req)
		if t == 'message':
			if k == 'greeting':
				msg = loaded.get('text', None) + ' ' + find_user(_id, token) + ''
				logger.info(message)
				api_request(_id, msg, token)
		elif t == 'quick':
			text = loaded.get('text', None)
			api_request(_id, text, message, token)
		else:
			pass 



	except AttributeError:
		logger.warning('Could not find handler for {}'.format(t))
	return True

def make_quiz_response(_id, idx, token):
	question = handle_quiz(idx)
	if not question:
		return False
	choices = question.get("choices", None)
	letters = ["A", "B", "C", "D"]
	answer = []

	answer.append(question.get("question"))

	for i in range(len(choices)):
		ans = '{} - {}\n'.format(letters[i], choices[i])
		answer.append(ans)

	logger.info(question)

	replies = []

	for i in range(len(letters)):
		reply = {}
		reply["content_type"] = "text"
		reply["title"] = letters[i]
		reply["payload"] = letters[i]
		print(reply)
		replies.append(reply)

	send_quick_replies(_id, ''.join(answer), replies, token)

	return True


def make_quick_replies(payload):
	replies = []

	for i in range(len(payload.get("options", None))):
		reply = {}
		reply["content_type"] = "text"
		reply["title"] = payload["options"][i]
		reply["payload"] = payload["payload"][i]
		print(reply)
		replies.append(reply)

	return replies


def make_postback_replies(payload):
	replies = []

	for i in range(len(payload.get("choices", None))):
		reply = {}

		reply["buttons"] = []
		reply["title"] = payload["choices"][i]
		
		print(reply)
		replies.append(reply)

	return replies


def make_message_replies(text):
	payload = {
		"message": text
	}

	return payload


def send_message_replies(_id, text, token):
	data = json.dumps({
		"recipient":{
			"id": _id
		},
		"message": {
			"text": text
		}
		})
	r = requests.post(graph.format(token), headers = headers, data = data)
	if r.status_code == 200:
		logger.info("Successfully made messages responses request!")
	else:
		logger.error('{} : {}'.format(r.status_code, r.text))



def send_quick_replies(_id, txt, msg, token):
	data = json.dumps({
		"recipient":{
			"id": _id
		},
		"message": {
			"text": txt,
			"quick_replies": msg
		}
		})
	r = requests.post(graph.format(token), headers = headers, data = data)
	if r.status_code == 200:
		logger.info("Successfully made quick responses request!")
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

def send_postback_replies(_id, txt, msg, token):
	data = json.dumps({
		"recipient":{
			"id": _id
		},
		"message":{
			"attachment":{
				"type":"template",
				"payload":{
					"template_type":"generic",
					"elements": [
						{
						"title": txt,
						"subtitle": "Stuff to come",
						"buttons": msg
						}
					]
				}
			}
			}
		})

	r = requests.post(graph.format(token), headers = headers, data = data)
	if r.status_code == 200:
		logger.info("Successfully made postback responses request!")
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

def import_questions():
    questions = {}
    try:
        with open(quiz_path, "r") as store:
            questions = json.load(store)
            store.close()
    except (IOError, OSError):
        return None

    return questions


def find_user(id, token):
    headers = {
    'Content-Type' : 'application/json'
    }
    r = requests.get('https://graph.facebook.com/v3.2/' + id + '?fields=first_name,last_name&access_token=' + token , headers = headers)
    nm = r.json()
    return nm['first_name']

 
def handle_quiz(idx):
	questions = import_questions()
	question = questions.get(str(idx + 1), None)
	return question

def check_answers(idx, ans):
	questions = import_questions()
	question = questions.get(str(idx + 1), None)
	chosen = letters.index(ans)
	score = question["answers"][chosen]

	return score

