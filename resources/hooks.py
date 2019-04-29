from flask import Flask, request, current_app
import json
import requests
import os
from . import bot
from .utilities import import_questions

PAT = os.environ.get('PAT', None)
verify_token = os.environ.get('VERIFY_TOKEN', None)

@bot.route('/', methods = ['GET'])
def worker_verification():
    pp = current_app.config.get("file")
    xx = import_questions(pp)
    print(xx)
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
    xx = import_questions()
    print(xx)
    try:
        if messages['object'] == 'page':
            for message in messages['entry']:
                for msg in message['messaging']:
                    if (msg.get('message')) or  (msg.get('postback')):
                        print(msg)
    except Exception as e:
        raise e

    return 'OK', 200

@bot.errorhandler(404)
def handle_error(ex):
    print(ex)
    print(request.url_rule.rule)

