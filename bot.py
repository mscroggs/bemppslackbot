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
    elif command == "oxmas":
        import sqlite3
        say("OXMAS!")
        oxmastime()
        oxmasql=sqlite3.connect('/home/pi/oxmas/oxmas.db')
        oxsql=oxmasql.cursor()
        for row in oxsql.execute("SELECT COUNT(*) FROM oxmas WHERE att=1"):
            n = str(row[0])
        say("The following "+str(n)+" people are coming to Oxmas:")
        saythis=[]
        for row in oxsql.execute("SELECT * FROM oxmas WHERE att=1"):
            saythis.append(row[1])
            if len(saythis)==5:
                say(", ".join(saythis))
                saythis=[]
        if saythis!=[]:
            say(", ".join(saythis))
        oxsql.close()
    elif command in ["santa","secretsanta"]:
        import sqlite3
        say("OXMAS!")
        oxmasql=sqlite3.connect('/home/pi/oxmas/oxmas.db')
        oxsql=oxmasql.cursor()
        for row in oxsql.execute("SELECT COUNT(*) FROM oxmas WHERE santa='yes' OR santa='sent'"):
            n = str(row[0])
        say("The following "+str(n)+" people are part of Oxmas secret santa:")
        saythis=[]
        for row in oxsql.execute("SELECT * FROM oxmas WHERE santa='yes' OR santa='sent'"):
            saythis.append(row[1])
            if len(saythis)==5:
                say(", ".join(saythis))
                saythis=[]
        if saythis!=[]:
            say(", ".join(saythis))
        oxsql.close()
    elif command in ["satan","secretsatan"]:
        say("Sorry, secret satan is cancelled this year...")
    elif command == "christmas":
        say("Did you mean \"?oxmas\"?")
    elif command == "drop" and args[0]=="tables":
        say("SUDO DROP CAMERON'S TABLES")
    elif command == "sudo":
        if args[0]=="christmas":
            say("CHRISTMAS!")
            xmastime()
        else:
            say("I don't know how to "+command+".")
    else:
        say("I don't know how to "+command+".")



def oxmasdatetime():
    today=datetime.datetime.today()
    today=datetime.datetime(today.year,today.month,today.day)
    xmas=datetime.datetime(today.year,12,25)
    xmasnextyear=datetime.datetime(today.year+1,12,25)

    oxmasdate=25-xmas.weekday()-2
    while oxmasdate>22:
        oxmasdate-=7

    noxmasdate=25-xmas.weekday()-2
    while noxmasdate>22:
        noxmasdate-=7

    oxmas=datetime.datetime(today.year,12,oxmasdate)

    rd=relativedelta(oxmas,today)

    if rd.__dict__['days']<0 or rd.__dict__['months']<0:
        oxmas=datetime.datetime(today.year+1,12,noxmasdate)
        rd=relativedelta(oxmas,today)
    return oxmas,rd
def xmasdatetime():
    today=datetime.datetime.today()
    today=datetime.datetime(today.year,today.month,today.day)
    xmas=datetime.datetime(today.year,12,25)

    rd=relativedelta(xmas,today)

    if rd.__dict__['days']<0 or rd.__dict__['months']<0:
        xmas=datetime.datetime(today.year+1,12,25)
        rd=relativedelta(xmas,today)
    return xmas,rd

def oxmastime():
    oxmas,rd = oxmasdatetime()
    say_days_til(rd)
def xmastime():
    oxmas,rd = xmasdatetime()
    say_days_til(rd,"Christmas")


def say_days_til(rd,oxmas="Oxmas"):
    sendme=""
    monfs="%(months)d" % rd.__dict__
    dayfs="%(days)d" % rd.__dict__
    if monfs=="0" and dayfs=="0":
        sendme=oxmas+" is today!!"
    else:
        if monfs!="0":
            sendme+=monfs+" month"
            if monfs!="1": sendme+="s"
            if dayfs!="0": sendme+=","
        if dayfs!="0":
            sendme+=" "+dayfs+" day"
            if dayfs!="1": sendme+="s"
        sendme+=" til "+oxmas
    say(sendme)


def parse_slack_output(output_list):
    global channel
    global AT_BOT
    for output in output_list:
        if output and 'text' in output and output['user']!=BOT_ID:
            channel=output['channel']
            text=output['text'].lower()
            if text == "scroggsbot?" or output['text']==AT_BOT+"?":
                say("<@"+output["user"]+">?")
            if text == "scroggsbot!" or output['text']==AT_BOT+"!":
                say("<@"+output["user"]+">!")
            print(text)
            if text[0] == "?":
                do_command(text[1:].lower())
            if "scorpions" in text:
                say(":scorpion:"*5)
            elif "scorpion" in text:
                say(":scorpion:")
            if "peter" in text:
                say("who?")
            if "oxmas" in text:
                say("OXMAS!")

slack_client = SlackClient(BOT_TOKEN)

if slack_client.rtm_connect():
    print("ScroggsBot connected and running!")
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
            with open("/home/pi/slackbot/log","a") as f:
                f.write(str(type(e))+" "+e.message+"\n")
            slack_client.api_call("chat.postMessage",channel="scroggsbot-dev", text="ERROR!", as_user=True)
            slack_client.api_call("chat.postMessage",channel="scroggsbot-dev", text=str(type(e))+" "+e.message, as_user=True)
            time.sleep(60)
        time.sleep(1)
