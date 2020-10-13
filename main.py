import threading
import traceback

import telebot

import RefreshDB
import config

import time
import handlers
import flask
from flask import Flask,request


# initialization of bot
from etc import bot
# initialization of flask app
app = Flask(__name__)



"""
    creation of flask site and webhook
"""

@app.route("/", methods=["HEAD","GET"])
def index():
    return ''

# steal from official github, setting the webhook to ngrock tunnel server
@app.route('/', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)



def RefreshDB_schedule(delay, task):
    next_time = time.time() + delay
    task()
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()

        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay

if __name__ == "__main__":
    # RUN
    threading.Thread(target=lambda: RefreshDB_schedule(24*60*60, RefreshDB.loop)).start()

    bot.remove_webhook()
    time.sleep(0.1)
    bot.set_webhook(config.NGROK)
    app.run()
