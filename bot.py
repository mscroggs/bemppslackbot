import os
import time
from slackclient import SlackClient
from dateutil.relativedelta import relativedelta
import datetime
from websocket._exceptions import WebSocketConnectionClosedException
import urllib2
from os import system

from config import *

def say(thing,overwritechan=None):
    global channel
    if overwritechan is not None:
        channel = overwritechan
    slack_client.api_call("chat.postMessage",channel=channel, text=thing, as_user=True)

def do_command(c):
    from random import randrange
    command = c.split(" ")[0]
    args = c.split(" ")[1:]
    if command in ["die","dice"]:
        say("I rolled a die and got a "+str(randrange(1,7)))
    elif command == "help":
        say("I am bemppbot. You can find my source code at https://github.com/mscroggs/bemppslackbot")
    elif command == "version":
        system("cd /home/pi/slackbot/bempp/bempp;git pull")
        with open("/home/pi/slackbot/bempp/bempp/VERSION") as f:
            say("master branch is currently at version "+f.read())

def check_for_commits():
    import json
    with open("/home/pi/slackbot/bempp/done") as f:
        done = json.load(f)
    from xml.etree import ElementTree
    feed = "https://bitbucket.org/bemppsolutions/bempp/rss"
    response = urllib2.urlopen(feed)
    xml = response.read()
    e = ElementTree.fromstring(xml)
    c = e.findall("channel")[0]
    more = None
    mess = None
    for i in c.findall("item"):
        guid = i.find("guid").text.strip()
        if guid not in done:
            title = i.find("title").text.strip()
            author = i.find("author").text.split("(")[1].split(")")[0]
            if more is None:
                mess = author+" pushed changes: "+", ".join(title.split("\n"))
                more = 0
            else:
                more += 1
            done.append(guid)
        if mess is not None:
            if more > 0:
                mess += " and "+str(more)+" other commits "
            say(mess,"general")
    with open("/home/pi/slackbot/bempp/done","w") as f:
        json.dump(done,f)


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
                check_for_commits()
            except KeyboardInterrupt:
                break
            except WebSocketConnectionClosedException:
                time.sleep(60)
                slack_client = SlackClient(BOT_TOKEN)
                slack_client.rtm_connect()
        except Exception as e:
            with open("/home/pi/slackbot/bempp/log","a") as f:
                f.write(str(type(e))+" "+e.message+"\n")
            print(str(type(e))+" "+e.message+"\n")
            time.sleep(60)
        time.sleep(1)
