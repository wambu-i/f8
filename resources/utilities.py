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

reviews = [
"Your company would seem to understand the commitment, strategies and resources needed to be a successful exporter. At the very least, you have a basis for beginning to export to the U.S.",
"Your company has a serious interest in exporting, but there are some areas of weakness in your export strategy that you should address if you want your export strategy to succeed. Careful consideration should be given, particularly to those questions that you scored low on, before embarking on an ambitious export strategy.",
"Your company is very weak in terms of preparing to export, and needs to do much more to ready itself for the U.S. market. There are considerable weaknesses, and if they are not addressed, it is highly unlikely that your export strategy will be successful."
]

headers = {
	'Content-Type' : 'application/json'
}

graph = "https://graph.facebook.com/v3.2/me/messages?access_token={}"
__all__ = ['make_response', 'import_questions', 'find_user', 'make_quiz_response', 'check_answers', 'get_index', 'score_answers']

_CURRENT_MODULE_ = sys.modules[__name__]

answers = []

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
	send_carousel(id, [
            {
                "title": "1. Prepare to export",
                "default_action": {
                    "type": "web_url",
                    "url": "f8-2019.firebaseapp.com/guide/export",
                    "webview_height_ratio": "tall",
                },
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "f8-2019.firebaseapp.com/guide/export",
                        "title": "Learn more"
                    }
                ]
            }, {
                "title": "2. Making the deal",
                "default_action": {
                    "type": "web_url",
                    "url": "f8-2019.firebaseapp.com/guide/deal",
                    "webview_height_ratio": "tall",
                },
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "f8-2019.firebaseapp.com/guide/deal",
                        "title": "Learn more"
                    }
                ]
            }, {
                "title": "3. Arranging the shipment",
                "default_action": {
                    "type": "web_url",
                    "url": "f8-2019.firebaseapp.com/guide/shipment",
                    "webview_height_ratio": "tall",
                },
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "f8-2019.firebaseapp.com/guide/shipment",
                        "title": "Learn more"
                    }
                ]
            }, {
                "title": "4. Exporting to the U.S.",
                "default_action": {
                    "type": "web_url",
                    "url": "f8-2019.firebaseapp.com/guide/export_us",
                    "webview_height_ratio": "tall",
                },
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "f8-2019.firebaseapp.com/guide/export_us",
                        "title": "Learn more"
                    }
                ]
            }, {
                "title": "5. Getting paid",
                "default_action": {
                    "type": "web_url",
                    "url": "f8-2019.firebaseapp.com/guide/payment",
                    "webview_height_ratio": "tall",
                },
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "f8-2019.firebaseapp.com/guide/payment",
                        "title": "Learn more"
                    }
                ]
            }, {
                "title": "6. Common Bill Errors",
                "default_action": {
                    "type": "web_url",
                    "url": "f8-2019.firebaseapp.com/guide/common_bill_errors",
                    "webview_height_ratio": "tall",
                },
                "buttons": [
                    {
                        "type": "web_url",
                        "url": "f8-2019.firebaseapp.com/guide/common_bill_errors",
                        "title": "Learn more"
                    }
                ]
            }
		], token)

def send_export_categories(id, token):
	send_carousel(id,
               [
                   {
                       "title": "Apparel Manufacturing",
                       "image_url": "https://agoa.info/images/articles/5183/_thumb4/southafrica_textileworker.jpg",
                       "default_action": {
                           "type": "web_url",
                           "url": "f8-2019.firebaseapp.com/regulations/apparel",
                           "webview_height_ratio": "tall",
                       },
                       "buttons": [
                           {
                               "type": "web_url",
                               "url": "f8-2019.firebaseapp.com/regulations/apparel",
                               "title": "View regulations"
                           }
                       ]
                   },
                   {
                       "title": "Cashews",
                       "image_url": "https://agoa.info/images/articles/5183/_thumb4/southafrica_textileworker.jpg",
                       #   "subtitle": "We have the right hat for everyone.",
                       "default_action": {
                           "type": "web_url",
                           "url": "f8-2019.firebaseapp.com/regulations/cashew",
                           "webview_height_ratio": "tall",
                       },
                       "buttons": [
                           {
                               "type": "web_url",
                               "url": "f8-2019.firebaseapp.com/regulations/cashew",
                               "title": "View regulations"
                           }
                       ]
                   },
                   {
                       "title": "Coffee",
                       "image_url": "https://agoa.info/images/articles/5156/_thumb4/coffee_tasters_ethiopia600_400.jpg",
                       #   "subtitle": "We have the right hat for everyone.",
                       "default_action": {
                           "type": "web_url",
                           "url": "https://f8-2019.firebaseapp.com/regulations/coffee",
                           "webview_height_ratio": "tall",
                       },
                       "buttons": [
                           {
                               "type": "web_url",
                               "url": "https://f8-2019.firebaseapp.com/regulations/coffee",
                               "title": "View regulations"
                           }
                       ]
                   },
                   {
                       "title": "Foodstuff",
                       "image_url": "https://agoa.info/images/articles/6214/_thumb4/foodagoa.jpg",
                       #   "subtitle": "We have the right hat for everyone.",
                       "default_action": {
                           "type": "web_url",
                           "url": "https://f8-2019.firebaseapp.com/regulations/foodstuff",
                           "webview_height_ratio": "tall",
                       },
                       "buttons": [
                           {
                               "type": "web_url",
                               "url": "https://f8-2019.firebaseapp.com/regulations/foodstuff?locale={}".format(locale),
                               "title": "View regulations"
                           }
                       ]
                   },
                   {
                       "title": "Textiles",
                       "image_url": "https://agoa.info/images/articles/5159/_thumb4/ethiopia_trad_textiles_collage_small.jpg",
                       #   "subtitle": "We have the right hat for everyone.",
                       "default_action": {
                           "type": "web_url",
                           "url": "https://f8-2019.firebaseapp.com/regulations/textiles",
                           "webview_height_ratio": "tall",
                       },
                       "buttons": [
                           {
                               "type": "web_url",
                               "url": "https://f8-2019.firebaseapp.com/regulations/textiles",
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
	return nm['locale']

def handle_quiz(_id, token, idx):
	logger.info(idx)
	language = get_language(_id, token)
	path = language + "_agoa.json"
	questions = import_questions(path)
	question = questions.get(str(idx + 1), None)
	return question

def check_answers(idx, ans):
	questions = import_questions()
	question = questions.get(str(idx + 1), None)
	chosen = letters.index(ans)
	logger.info(chosen)
	logger.info((question["answers"]))
	score = question["answers"][chosen]

	return score

def score_answers(_id, token):
	final = 0
	answered = []
	with open(ans_path, "r") as answers:
		lines = answers.readlines()
		answers.close()
		logger.info(lines)

	for i in range(len(lines)):
		score = lines[i].split(" ")[1]
		logger.info(score)
		final += int(score.strip('\n'))

	message = "You scored {}".format(final)
	rev = None

	if final > 80:
		rev = reviews[0]
	elif final > 47 and final < 80:
		rev = reviews[1]
	else:
		rev = reviews[2]

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
