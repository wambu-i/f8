from flask import Flask, request, current_app
import json
import requests
import os
from . import bot
from .utilities import (import_questions, make_response, find_user)

PAT = os.environ.get('PAT', None)
verify_token = os.environ.get('VERIFY_TOKEN', None)

@bot.route('/', methods = ['GET'])
def worker_verification():
    make_response("text", "introduction")
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
    try:
        messages = request.get_json()
        if messages['object'] == 'page':
            for message in messages['entry']:
                for msg in message['messaging']:
                    if (msg.get('message')) or  (msg.get('postback')):
                        sender_id = msg['sender']['id']
                        user = find_user(sender_id, PAT)

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

