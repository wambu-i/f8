from flask import Flask, request, current_app
import json
import requests
import os
from . import bot
from .utilities import (import_questions, make_response, make_quiz_response, find_user)

PAT = os.environ.get('PAT', None)
verify_token = os.environ.get('VERIFY_TOKEN', None)

answers = []
letters = ["A", "B", "C", "D"]

@bot.route('/', methods = ['GET'])
def worker_verification():
    if PAT is not None and verify_token is not None:
        if request.args.get('hub.verify_token', '') == verify_token:
            print("Verification successful!")
            return request.args.get('hub.challenge', '')
        else:
            print("Verification failed!")
            return 'Error, wrong validation token'
    else:
        return "Could not get verification tokens."


@bot.route('/', methods = ['POST'])
def worker_messaging():
    global quizzing
    quizzing = False
    try:
        messages = request.get_json()
        if messages['object'] == 'page':
            for message in messages['entry']:
                for msg in message['messaging']:
                    print(msg)
                    if (msg.get('message')) or  (msg.get('postback')):
                        sender_id = msg['sender']['id']
                        user = find_user(sender_id, PAT)
                        idx = len(answers)

                        if (msg.get('message', None)):
                            received = msg['message']
                            if (received.get('quick_reply', None)):
                                txt = received['quick_reply']['payload']
                                print(txt)
                                if txt == 'quiz':
                                    quizzing = True
                                    print("Creating quiz!")
                                    make_quiz_response(sender_id, idx, PAT)
                                elif txt in letters and quizzing is True:
                                    score = check_answers(idx, txt)
                                    answers.append((txt, score))
                                    print(answers)
                            else:
                                txt = received["text"]
                                if txt in letters and quizzing is True:
                                    score = check_answers(idx, txt)
                                    answers.append((txt, score))
                                    print(answers)

                        if msg.get('postback'):
                            received = msg['postback']['payload']
                            if received == 'start':
                                make_response(sender_id, 'message', 'greeting', PAT)
                                make_response(sender_id, 'quick', 'introduction', PAT)
    except Exception as e:
        raise e

    return 'OK', 200

@bot.errorhandler(404)
def handle_error(ex):
    print(ex)
    print(request.url_rule.rule)



