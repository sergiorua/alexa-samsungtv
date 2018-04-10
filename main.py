#!/usr/bin/env python

import os
import logging
import samsungctl
import re
from flask import Flask
from flask_ask import Ask, statement, question, session

DEBUG = True
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = DEBUG
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
#logging.basicConfig(level=logging.DEBUG
#                    format='%(asctime)s %(levelname)s %(message)s',
#                    filename='/tmp/myapp.log',
#                    filemode='w')

remoteConfig = {
    "name": "samsungctl",
    "description": "PC",
    "id": "sergVoiceRemote",
    "host": "192.168.0.13",
    "port": 55000,
    "method": "legacy",
    "timeout": 1,
}
RemoteKeyMap = {
    'volume up': 'KEY_VOLUP',
    'volume down': 'KEY_VOLDOWN',
    'channel %d': 'KEY_%d',
    'channel up': 'KEY_UP',
    'channel down': 'KEY_DOWN',
    'power off': 'KEY_POWEROFF'
}

def press_remote_key(key_pressed):
    Remote = samsungctl.Remote(remoteConfig)
    k = key_pressed.lower()
    if re.match('channel (\d+)', k):
        n = int(re.match('channel (\d+)', 'channel 5').groups()[0])
        k_code = 'KEY_%d' % (n)
    else:
        k_code = RemoteKeyMap[k]

    return Remote.control(k_code)

    

@ask.launch
def start_skill():
    welcome_message = 'Hello to Samsung TV Remote'
    return statement(welcome_message)

@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("Goodbye")

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Goodbye")

@ask.session_ended
def session_ended():
    return "{}", 200

@ask.intent('tvButtonPressed',
    mapping={
        'key': 'Key',
        'direction': 'Direction'
    })
def tv_button_pressed(key, direction):
    k=key + " " +direction
    press_remote_key(k)
    return statement("ok").simple_card('tvButtonPressedReply', "ok")

if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=DEBUG)

# vim: ts=4 expandtab