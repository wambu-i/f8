import json
import os

import logging
import requests
import sys

formatter = '[%(asctime)-15s] %(levelname)s [%(filename)s.%(funcName)s#L%(lineno)d] - %(message)s'

logging.basicConfig(level = logging.DEBUG, format = formatter)

letters = ["A", "B", "C", "D"]
booleans = ["Yes", "No"]

# Create logger instance
logger = logging.getLogger('api')
resp_path = os.path.abspath("responses.json")
ans_path = os.path.abspath("answers.txt")

assets = {
	"quick": {
		"usage" : ["introduction"],
		"type" : "quick_replies"
	},
	"message" : {
		"type": "text"
	}
}

en_reviews = [
"Your company would seem to understand the commitment, strategies and resources needed to be a successful exporter. At the very least, you have a basis for beginning to export to the U.S.",
"Your company has a serious interest in exporting, but there are some areas of weakness in your export strategy that you should address if you want your export strategy to succeed. Careful consideration should be given, particularly to those questions that you scored low on, before embarking on an ambitious export strategy.",
"Your company is very weak in terms of preparing to export, and needs to do much more to ready itself for the U.S. market. There are considerable weaknesses, and if they are not addressed, it is highly unlikely that your export strategy will be successful."
] 

fr_reviews = [
	"Votre entreprise semble comprendre l’engagement, stratégies et ressources nécessaires pour réussir à exporter. En tout cas, vous avez une base pour commencer à exporter aux États-Unis.",
	"Votre entreprise a un intérêt sérieux à exporter, mais il existe quelques faiblesses dans votre stratégie d’exportation que vous devriez aborder si vous voulez que votre stratégie d'exportation réussisse. Une considération attentive devrait être donnée, en particulier aux questions que vous avez marqué faible avant de se lancer dans une stratégie d'exportation ambitieuse."
	"Votre entreprise est très faible en termes de préparation à l’exportation et doit faire beaucoup plus pour se préparer au marché américain. Il y a faiblesses considérables, et si elles ne sont pas abordées, il est hautement peu probable que votre stratégie d'exportation soit couronnée de succès."
]

headers = {
	'Content-Type' : 'application/json'
}

graph = "https://graph.facebook.com/v3.2/me/messages?access_token={}"
__all__ = ['make_response', 'import_questions', 'find_user', 'make_quiz_response', 'check_answers', 'get_index', 'score_answers', 'send_message_replies']

_CURRENT_MODULE_ = sys.modules[__name__]

answers = []

def get_response(path):
	responses = {}
	print(resp_path)
	try:
		with open(path, "r") as store:
			responses = json.load(store)
			store.close()
	except (IOError, OSError):
		return responses
	return responses

def make_response(_id, t, k, token, **kwargs):
	loaded = None
	message = None

	language = get_language(_id, token)
	path = language + "_responses.json"
	response = get_response(path)
	if response:
		loaded = response.get(k, None)
	else:
		return None
	if not loaded:
		logger.error("Could not find specified option in provided responses.")
		return None

	handler_name = 'make_{}_replies'.format(t)
	req = 'send_{}_replies'.format(t)
	#logger.info(handler_name, req)
	_type = assets[t]["type"]
	try:
		handler = getattr(_CURRENT_MODULE_, handler_name)
		message = handler(loaded)
		api_request = getattr(_CURRENT_MODULE_, req)
		if t == 'message':
			if k == 'greeting':
				msg = loaded.get('text', None) + ' ' + find_user(_id, token) + '!'
				logger.info(message)
				api_request(_id, msg, token)
				api_request(_id, loaded["description"], token)
		elif t == 'quick':
			text = loaded.get('text', None)
			api_request(_id, text, message, token)
		else:
			pass

	except AttributeError:
		logger.warning('Could not find handler for {}'.format(t))
	return True

def make_quiz_response(_id, idx, token):
	question = handle_quiz(_id, token, idx)
	if not question:
		return False
	choices = question.get("choices", None)
	answer = []

	answer.append(question.get("question") + '\n')

	for i in range(len(choices)):

		ans = '{} - {}\n'.format(letters[i], choices[i])
		answer.append(ans)

	logger.info(question)

	replies = []

	for i in range(len(choices)):
		reply = {}
		reply["content_type"] = "text"
		if len(choices) > 2:
			reply["title"] = letters[i]
		else:
			reply["title"] = booleans[i]

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


def send_guide_options(id, token):
	language = get_language(id, token)[:2]
	send_carousel(id, [
		{
			"title": "1. Prepare to export",
			"default_action": {
				"type": "web_url",
				"url": "https://f8-2019.firebaseapp.com/{}/guide/export".format(language),
				"webview_height_ratio": "tall",
			},
			"buttons": [
				{
					"type": "web_url",
					"url": "https://f8-2019.firebaseapp.com/{}/guide/export".format(language),
					"title": "Learn more"
				}
			]
		}, {
			"title": "2. Making the deal",
			"default_action": {
				"type": "web_url",
				"url": "https://f8-2019.firebaseapp.com/{}/guide/deal".format(language),
				"webview_height_ratio": "tall",
			},
			"buttons": [
				{
					"type": "web_url",
					"url": "https://f8-2019.firebaseapp.com/{}/guide/deal".format(language),
					"title": "Learn more"
				}
			]
		}, {
			"title": "3. Arranging the shipment",
			"default_action": {
				"type": "web_url",
				"url": "https://f8-2019.firebaseapp.com/{}/guide/shipment".format(language),
				"webview_height_ratio": "tall",
			},
			"buttons": [
				{
					"type": "web_url",
					"url": "https://f8-2019.firebaseapp.com/{}/guide/shipment".format(language),
					"title": "Learn more"
				}
			]
		}, {
			"title": "4. Exporting to the U.S.",
			"default_action": {
				"type": "web_url",
				"url": "https://f8-2019.firebaseapp.com/{}/guide/export_us".format(language),
				"webview_height_ratio": "tall",
			},
			"buttons": [
				{
					"type": "web_url",
					"url": "https://f8-2019.firebaseapp.com/{}/guide/export_us".format(language),
					"title": "Learn more"
				}
			]
		}, {
			"title": "5. Getting paid",
			"default_action": {
				"type": "web_url",
				"url": "https://f8-2019.firebaseapp.com/{}/guide/payment".format(language),
				"webview_height_ratio": "tall",
			},
			"buttons": [
				{
					"type": "web_url",
					"url": "https://f8-2019.firebaseapp.com/{}/guide/payment".format(language),
					"title": "Learn more"
				}
			]
		}, {
			"title": "6. Common Bill Errors",
			"default_action": {
				"type": "web_url",
				"url": "https://f8-2019.firebaseapp.com/{}/guide/common_bill_errors".format(language),
				"webview_height_ratio": "tall",
			},
			"buttons": [
				{
					"type": "web_url",
					"url": "https://f8-2019.firebaseapp.com/{}/guide/common_bill_errors".format(language),
					"title": "Learn more"
				}
			]
		}
	], token)


def send_export_categories(id, token):
	language = get_language(id, token)[:2]
	send_carousel(id,
				  [
					  {
						  "title": "Cheese, milk and dairy products",
						  "default_action": {
							  "type": "web_url",
							  "url": "https://f8-2019.firebaseapp.com/{}/regulations/cheese".format(language),
							  "webview_height_ratio": "tall",
						  },
						  "buttons": [
							  {
								  "type": "web_url",
								  "url": "https://f8-2019.firebaseapp.com/{}/regulations/cheese".format(language),
								  "title": "View regulations"
							  }
						  ]
					  },
					  {
						  "title": "Fruits, vegetables and nuts",
						  "default_action": {
							  "type": "web_url",
							  "url": "https://f8-2019.firebaseapp.com/{}/regulations/fruits".format(language),
							  "webview_height_ratio": "tall",
						  },
						  "buttons": [
							  {
								  "type": "web_url",
								  "url": "https://f8-2019.firebaseapp.com/{}/regulations/fruits".format(language),
								  "title": "View regulations"
							  }
						  ]
					  },
					  {
						  "title": "Livestock and animals",
						  "default_action": {
							  "type": "web_url",
							  "url": "https://f8-2019.firebaseapp.com/{}/regulations/livestock".format(language),
							  "webview_height_ratio": "tall",
						  },
						  "buttons": [
							  {
								  "type": "web_url",
								  "url": "https://f8-2019.firebaseapp.com/{}/regulations/livestock".format(language),
								  "title": "View regulations"
							  }
						  ]
					  },
					  {
						  "title": "Meat, poultry, and meat or poultry products",
						  "default_action": {
							  "type": "web_url",
							  "url": "https://f8-2019.firebaseapp.com/{}/regulations/meat".format(language),
							  "webview_height_ratio": "tall",
						  },
						  "buttons": [
							  {
								  "type": "web_url",
								  "url": "https://f8-2019.firebaseapp.com/{}/regulations/meat".format(language),
								  "title": "View regulations"
							  }
						  ]
					  },
					  {
						  "title": "Plant and plant products",
						  "default_action": {
							  "type": "web_url",
							  "url": "https://f8-2019.firebaseapp.com/{}/regulations/plants".format(language),
							  "webview_height_ratio": "tall",
						  },
						  "buttons": [
							  {
								  "type": "web_url",
								  "url": "https://f8-2019.firebaseapp.com/{}/regulations/plants".format(language),
								  "title": "View regulations"
							  }
						  ]
					  },
							   {
						  "title": "Seeds",
						  "default_action": {
							  "type": "web_url",
							  "url": "https://f8-2019.firebaseapp.com/{}/regulations/seeds".format(language),
							  "webview_height_ratio": "tall",
						  },
						  "buttons": [
							  {
								  "type": "web_url",
								  "url": "https://f8-2019.firebaseapp.com/{}/regulations/seeds".format(language),
								  "title": "View regulations"
							  }
						  ]
					  },
				  ],
				  token)


def send_carousel(id, payload, token):
	data = json.dumps({
"recipient":{
	"id": id
  },
  "message":{
	"attachment":{
	  "type":"template",
	  "payload":{
		"template_type":"generic",
		"elements": payload
	  }
	}
  }
		})

	r = requests.post(graph.format(token), headers = headers, data = data)
	if r.status_code == 200:
		logger.info("Successfully made postback responses request!")
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

def send_postback_replies(_id, txt, buttons, token):
	data = json.dumps({
		"recipient":{
			"id": _id
		},
		"message":{
			"attachment":{
				"type":"template",
				"payload":{
					"template_type":"button",
					"text": txt,
					"buttons": buttons
				}
			}
			}
		})

	r = requests.post(graph.format(token), headers = headers, data = data)
	if r.status_code == 200:
		logger.info("Successfully made postback responses request!")
	else:
		logger.error('{} :{}'.format(r.status_code, r.text))

def import_questions(path):
	questions = {}
	try:
		with open(path, "r") as store:
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

def get_language(id, token):
	headers = {
		'Content-Type' : 'application/json'
	}

	r = requests.get('https://graph.facebook.com/v3.2/' + id + '?fields=locale&access_token=' + token, headers = headers)
	nm = r.json()
	print(nm)
	return nm['locale'][:2]

def handle_quiz(_id, token, idx):
	logger.info(idx)
	language = get_language(_id, token)
	path = language + "_agoa.json"
	questions = import_questions(path)
	question = questions.get(str(idx + 1), None)
	return question

def check_answers(_id, token, idx, ans):
	language = get_language(_id, token)
	path = language + "_agoa.json"
	questions = import_questions(path)
	question = questions.get(str(idx + 1), None)
	chosen = letters.index(ans)
	logger.info(chosen)
	logger.info((question["answers"]))
	score = question["answers"][chosen]

	return score

def score_answers(_id, token):
	final = 0
	answered = []
	language = get_language()
	with open(ans_path, "r") as answers:
		lines = answers.readlines()
		answers.close()
		logger.info(lines)

	for i in range(len(lines)):
		score = lines[i].split(" ")[1]
		logger.info(score)
		final += int(score.strip('\n'))

	message = "You scored {}".format(final)
	
	if language = "fr":
		message = "Tu as marqué {} points".format(points)

	rev = None

	if final > 18:
		rev = reviews[0]
		if language = "fr":
			rev = fr_reviews[0]
	elif final > 17 and final < 10:
		rev = reviews[1]
		if language = "fr":
			rev = fr_reviews[1]
	else:
		rev = reviews[2]
		if language = "fr":
			rev = fr_reviews[2]

	send_message_replies(_id, message, token)
	send_message_replies(_id, rev, token)


def get_index():
	idx = None
	with open(ans_path, "r") as f:
		lines = f.readlines()
		print(lines)
		idx = len([l for l in lines if l.strip(' \n') != ''])
		f.close()
	print(idx)
	return idx
