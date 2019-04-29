import sys
from resources import bot
from flask import Flask
from flask_cors import CORS, cross_origin

def setup():
    application = Flask(__name__)
    application.register_blueprint(bot, url_prefix = '/messenger/')
    CORS(application)
    return application


if __name__ == '__main__':
    app = setup()
    app.config['file'] = sys.argv[1]
    app.run()
