# coding: utf-8

dummy = "***"*100
'''
has globals : primary_key
'''

import os,random
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from flask import Flask, request, send_from_directory, render_template
import pickle
import messenger
from config import CONFIG
from fbpage import page
import spur
from fbmq import Attachment,Template,QuickReply
import pandas as pd
import json

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])
def validate():
    if request.args.get('hub.mode', '') == 'subscribe' and \
                    request.args.get('hub.verify_token', '') == CONFIG['VERIFY_TOKEN']:

        print("Validating webhook")

        return request.args.get('hub.challenge', '')
    else:
        return 'Failed validation. Make sure the validation tokens match.'

page.show_starting_button("START_PAYLOAD")       # Getting Started

@page.callback(['START_PAYLOAD'])
def start_callback(payload, event):
    sender_id = event.sender_id
    quick_replies = [
            QuickReply(title="Yeah !", payload="PICK_SYNC"),
            QuickReply(title="Nah ", payload="PICK_DSYNC")
            ]
    page.send(sender_id, "Would you like to sync this conversation ?\n you can subscribe etc. ",quick_replies=quick_replies,metadata="DEVELOPER_DEFINED_METADATA")
    print("Let's start!")

@page.callback(['PICK_SYNC', 'PICK_DSYNC'])
def callback_picked_genre(payload, event):
    sender_id = event.sender_id
    if payload == "PICK_SYNC":
        page.send(sender_id,"Please Share your *Briefly* username \n ( format id: username ) ")      # TODO
    else:
        page.send(sender_id,"Go ahead ;) Play Around for some time ")

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    print(payload)
    page.show_persistent_menu([Template.ButtonPostBack('SUB_LIST1', 'MENU_PAYLOAD/1'),
                           Template.ButtonPostBack('SUB_LIST2', 'MENU_PAYLOAD/2')])
    page.handle_webhook(payload,message = message_handler)

    return "ok"

@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    # try Menu
    buttons = [
        Template.ButtonWeb("Open Web URL", "https://www.codeforces.com"),
        Template.ButtonPostBack("Subscribe", "www.nytimes.com"),
        Template.ButtonPhoneNumber("Call Phone Number", "+91")
    ]

    user_profile = page.get_user_profile(sender_id)

    page.typing_on(sender_id)
    page.typing_off(sender_id)

    #print(user_profile)
    if "help" not in message.lower():
        try :
            # run command
            hostname,username,password = getUser(sender_id)
            shell_commands(hostname,username,password)
            page.send(sender_id,"Running ssh commmand")
            print("Bot results!")
        except:
            quick_replies = [
            QuickReply(title="Yeah !", payload="PICK_SSH"),
            QuickReply(title="Nah ", payload="PICK_SSH")
            ]
    page.send(sender_id, "Would you like to configure your ssh ",quick_replies=quick_replies,metadata="DEVELOPER_DEFINED_METADATA")
            page.send(sender_id,"Error Occured: try `help` ")
    elif "username" in message.lower():
        try:
            hostname,username, password= message.split()
            hostname = hostname.index("hostname")
            password = password.index("password")
            username = username.index("username")
        except:
            print("Some Error occured ;(")
    else:
        page.send(sender_id,"Provide Help: Carousel")
    
@page.callback(['PICK_SSH', 'PICK_SSH'])
def callback_picked_genre(payload, event):
    sender_id = event.sender_id
    if payload == "PICK_SSH":
        page.send(sender_id,"Please Share your credentials \n ( format id: username hostname password ) ")      # TODO
    else:
        page.send(sender_id,"That's just fine")


@page.callback(['MENU_PAYLOAD/(.+)'])
def click_persistent_menu(payload, event):
    click_menu = payload.split('/')[1]
    page.send(event.sender_id,"you clicked %s menu" % (click_menu))


# @app.route('/authorize', methods=['GET'])
# def authorize():
#     account_linking_token = request.args.get('account_linking_token', '')
#     redirect_uri = request.args.get('redirect_uri', '')

#     auth_code = '1234567890'

#     redirect_uri_success = redirect_uri + "&authorization_code=" + auth_code

#     return render_template('authorize.html', data={
#         'account_linking_token': account_linking_token,
#         'redirect_uri': redirect_uri,
#         'redirect_uri_success': redirect_uri_success
#     })

# # only issue , sends blobs
# ##@app.before_first_request
# def bot(text_message,sender_id):

#     Access_token = "8f88a5431e7d4bc1b07470b6e3eeee7d"
#     client = apiai.ApiAI(Access_token)
#     print("="*100)
#     req = client.text_request()
#     req.lang = "de"
#     req.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
#     req.query = text_message
#     response = json.loads(req.getresponse().read().decode('utf-8'))
#     responseStatus = response['status']['code']

#     if responseStatus==200 :
#         text = response['result']['fulfillment']['speech']
#     else:
#         text="No Match Found"

#     if len(response['result']['contexts']):
#         context = response['result']['contexts'][0]['parameters'] #extract parameters
#         Query = context['type'] #get the type of query
#         shorten_name = context['News'] #get the value of news
#         print(context)
#         if Query == "subscribe" :
#             text = "added "+shorten_name+" to your feed"
#             page.send(sender_id,text)
#             #print(type(sender_id))
#             #print(shorten_name)
#             #subscribe.subChannel(str(sender_id),shorten_name)
#         elif Query == "unsubscribe":
#             text = "removing "+shorten_name+" from your feed"
#             page.send(sender_id,text)
#             #subscribe.unsubChannel(str(sender_id),shorten_name)
#         elif Query == "summary":
#             text="generating your summary"
#             page.send(sender_id,text)
#             url = text_message.split()[-1]
#             if 'http' not in url:
#                 url='https://'+url
#             sumar = ""
#             for h in headline:
#                 sumar += h
#             text = title+" \n "+sumar
#             page.send(sender_id,text)
#         elif Query == "id":
#             user_name = text_message.split()[-1]
#             #subscribe.addUser(sender_id,user_name)
#             text = "You've been synced "
#             page.send(sender_id,text)
#             print("User Added")
#         else:
#             print("here")
#             text="loading the latest news from "+shorten_name
#             page.send(sender_id,text)
#             # page.send(sender_id,"Entity : %s \nValue : %s \nConfidence : %s "%(entin[0],result[entin[0]][0]['value'],result[entin[0]][0]['confidence']*100))
#             if results == False:
#                 return False
#             # gen articles send 1st
#             page.send(sender_id,Template.Generic(results))

#             # page.send(sender_id, Template.Buttons(results[1][:200],results[2]))
#         return True
#     else:
#         page.send(sender_id,text)
#         return True
#         '''
#         ListView Template
#         page.send(sender_id,Template.List(elements = results,top_element_style='large',
#             buttons=[
#                 { "title": "View Less", "type": "postback", "payload": "payload"}]))
#         '''

def shell_commands():
    shell = spur.SshShell(hostname="", username="", password="",missing_host_key=spur.ssh.MissingHostKey.accept)
    with shell:
        result = shell.run(["ls"])
    print(result.output) # PARSE

# Triggered off "PostBack Called"
@page.callback(['DEVELOPED_DEFINED_PAYLOAD(.+)'],types=['POSTBACK'])
def callback_clicked_button(payload,event):
    sender_id = event.sender_id
    news_id = int(payload[25:])      # bug
    print(dummy)
    print(news_id)
    # do something with these text   -> To add Headline
    page.send(sender_id,Attachment.Image(image_url))
    page.send(sender_id,summ_ary)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True,debug=True,use_reloader=False)
