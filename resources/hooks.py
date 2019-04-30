from flask import Flask, request, current_app
import json
import requests
import os
from . import bot
from .utilities import (import_questions, make_response, make_quiz_response, 
    find_user, check_answers, get_index, send_export_categories, 
    send_guide_options, score_answers, send_message_replies)

PAT = os.environ.get('PAT', None)
verify_token = os.environ.get('VERIFY_TOKEN', None)

letters = ["A", "B", "C", "D"]
countries = ["Kenya", "Sierra Leone", "Zambia", "Mozambique", "Togo"],

answers = os.path.abspath("answers.txt")
quizzing = False

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

#idx = get_index()

@bot.route('/', methods = ['POST'])
def worker_messaging():
    try:
        messages = request.get_json()
        if messages['object'] == 'page':
            for message in messages['entry']:
                for msg in message['messaging']:
                    print(msg)
                    idx = 0
                    print("Index is ", idx)

                    if (msg.get('message')) or  (msg.get('postback')):
                        sender_id = msg['sender']['id']
                        user = find_user(sender_id, PAT)

                        if msg.get('postback'):
                            received = msg['postback']['payload']
                            if received == 'start':
                                make_response(sender_id, 'message', 'greeting', PAT)
                                make_response(sender_id, 'message', 'description', PAT)
                                make_response(sender_id, 'quick', 'introduction', PAT)

                            if received == 'original':
                                make_response(sender_id, 'message', 'greeting', PAT)
                                make_response(sender_id, 'message', 'description', PAT)
                                make_response(sender_id, 'quick', 'introduction', PAT)
                                make_response(sender_id, 'quick', 'location', PAT)


                        if (msg.get('message')):
                            received = msg['message']
                            if (received.get('quick_reply', None)):
                                txt = received['quick_reply']['payload']
                                print("Here's the text ", txt)
                                if txt == 'quiz':
                                    print("Creating quiz!")
                                    with open(answers, "w") as store:
                                        store.close()
                                    make_quiz_response(sender_id, idx, PAT)
                                    with open(answers, "r") as xx:
                                        lines = xx.readlines()
                                        print(lines)

                                elif txt in letters:
                                    print("heres the choice ", txt)

                                    idx = get_index()

                                    if idx == 4:
                                        score_answers(sender_id, PAT)
                                        make_response(sender_id, 'quick', 'continue', PAT)
                                        continue

                                    score = check_answers(sender_id, PAT, idx, txt)
                                    with open(answers, "a") as store:
                                        print("Write to file %d", score)
                                        line = '{} {}\n'.format(txt, score)
                                        store.write(line)
                                        store.close()
                                    #print(answers)

                                    make_quiz_response(sender_id, idx + 1 , PAT)
                                elif txt in countries:
                                    if txt.lower() is not "kenya":
                                        send_message_replies(sender_id, "Sorry! We only support Kenya in this iteration!", PAT)
                                elif txt == 'guides':
                                    send_guide_options(sender_id, PAT)
                                    make_response(sender_id, 'quick', 'continue', PAT)
                                elif txt == 'categories':
                                    send_export_categories(sender_id, PAT)
                                    make_response(sender_id, 'quick', 'continue', PAT)
                            else:
                                make_response(sender_id, 'quick', 'introduction', PAT)

    except Exception as e:
        raise e

    return 'OK', 200

@bot.errorhandler(404)
def handle_error(ex):
    print(ex)
    print(request.url_rule.rule)


def make_quiz():
    quizzing = True
