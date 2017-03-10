import os
import time
from slackclient import SlackClient
from dateutil.relativedelta import relativedelta
import datetime
from websocket._exceptions import WebSocketConnectionClosedException

from config import *

def say(thing):
    global channel
    slack_client.api_call("chat.postMessage",channel=channel, text=thing, as_user=True)

def do_command(c):
    from random import randrange
    command = c.split(" ")[0]
    args = c.split(" ")[1:]
    if command in ["die","dice"]:
        say("I rolled a die and got a "+str(randrange(1,7)))
    elif command == "help":
        say("I am bemppbot. You can find my source code at https://github.com/mscroggs/bemppslackbot")



def parse_slack_output(output_list):
    global channel
    global AT_BOT
    for output in output_list:
        if output and 'text' in output and output['user']!=BOT_ID:
            channel=output['channel']
            text=output['text'].lower()
            if text == "bemppbot?" or output['text']==AT_BOT+"?":
                say("<@"+output["user"]+">?")
            if text == "bemppbot!" or output['text']==AT_BOT+"!":
                say("<@"+output["user"]+">!")
            print(text)
            if text[0] == "?":
                do_command(text[1:].lower())
            if "scorpions" in text:
                say(":scorpion:"*5)
            elif "scorpion" in text:
                say(":scorpion:")

slack_client = SlackClient(BOT_TOKEN)

if slack_client.rtm_connect():
    print("BemppBot connected and running!")
    while True:
        try:
            try:
                parse_slack_output(slack_client.rtm_read())
            except KeyboardInterrupt:
                break
            except WebSocketConnectionClosedException:
                time.sleep(60)
                slack_client = SlackClient(BOT_TOKEN)
                slack_client.rtm_connect()
        except Exception as e:
            with open("/home/pi/slackbot/bempp/log","a") as f:
                f.write(str(type(e))+" "+e.message+"\n")
            time.sleep(60)
        time.sleep(1)
