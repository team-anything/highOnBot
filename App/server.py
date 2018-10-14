# coding: utf-8

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
import paramiko,spur
from fbmq import Attachment,Template,QuickReply
import pandas as pd
from query import * 
import json
import fbmq


app = Flask(__name__)

def debug(i):
    print("="+str(i)*100)



@app.route('/webhook', methods=['GET'])
def validate():
    #shell_commands(hostname="192.168.14.189",username="Nishchith",password="@randombits98",command="ls")
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
            QuickReply(title="Yeah !", payload="PICK_CONF"),
            QuickReply(title="Nah ", payload="PICK_NCONF")
            ]
    page.send(sender_id, "Would you like to configure your ssh ",quick_replies=quick_replies,metadata="DEVELOPER_DEFINED_METADATA")
    print("Let's start!")

@page.callback(['PICK_CONF', 'PICK_NCONF'])
def callback_picked_genre(payload, event):
    sender_id = event.sender_id
    if payload == "PICK_CONF":
        page.send(sender_id,"Please Share your credentials \n ( format id: username hostname password ) ")      # TODO
    else:
        page.send(sender_id,"Go ahead ;) Play Around for some time ")

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)

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
    print("="*100)

    if "username" in message.lower():
        hostname,username, password = message.split("\n")
        hostname = hostname[9:]
        password = password[9:]
        username = username[9:]

        print(hostname,username,password,sender_id)
        current_path =  str(shell_commands(hostname,username,password,"pwd").decode("utf-8"))[:-1]
        addUser(sender_id,hostname,username,password,current_path)

        page.send(sender_id,"Go Ahead! Have Fun! ")
    elif "help" in message:
        page.send(sender_id, "Just 3 easy steps to follow 🚶")
        page.send(sender_id, Template.Generic([
            Template.GenericElement("Connect 🤝",subtitle="",item_url="",image_url="https://i.imgur.com/xXy4kib.png",buttons=[Template.ButtonWeb("Step 1", "https://www.oculus.com/en-us/rift/")]),
            Template.GenericElement("Add ➕",subtitle="",item_url="",image_url="https://i.imgur.com/RzjPKZM.png",buttons=[Template.ButtonWeb("Step 2", "https://www.oculus.com/en-us/rift/")]),
            Template.GenericElement("Go ✅",subtitle="",item_url="",image_url="https://i.imgur.com/NmNXnc7.png",buttons=[Template.ButtonWeb("Step 3", "https://www.oculus.com/en-us/rift/")])]))    
    else:
        response = getUser(sender_id)

        if not response:
            quick_replies = [
                QuickReply(title="Yeah !", payload="PICK_SSH"),
                QuickReply(title="Nah ", payload="PICK_NSSH")
                ]
            page.send(sender_id, "Would you like to configure your ssh ",quick_replies=quick_replies,metadata="DEVELOPER_DEFINED_METADATA")
        else:
            # print(hostname,username,password,message)
            hostname,username,password,current_path = response

            if message[:2] == "cd":
                # add cd
                need_path = message[3:]
                current_path = os.path.join(current_path,need_path)
                try:
                    new_path =  str(shell_commands(hostname,username,password,"cd "+current_path+"; pwd").decode("utf-8"))[:-1]
                    updatePath(sender_id,new_path)
                    page.send(sender_id,"Your Current Directory:\n"+new_path)
                except:                    
                    page.send(sender_id,"Path doesn't exist")
            elif "send" in message:
                file_name = message.split()[-1]
                if send_commands(current_path+"/"+file_name,file_name,hostname,username,password):
                    debug(659)
                    print(CONFIG['SERVER_URL']+"/"+file_name)
                    os.rename("./"+file_name, "./static/"+file_name)
                    page.send(sender_id,"Here You Go!")
                    page.send(sender_id, Attachment.File(CONFIG['SERVER_URL']+"/static/"+file_name))
                else:
                    page.send(sender_id, "Error Accessing the file !!")
            elif message!="Nah ":
                try:
                    result = str(shell_commands(hostname,username,password,"cd "+current_path+"; "+message).decode("utf-8"))
                    result = result[:min(150,len(result))]
                    page.send(sender_id,result)
                except:
                    page.send(sender_id,"Unknown Output!")

            print("Bot results!")
    
@page.callback(['PICK_SSH', 'PICK_NSSH'])
def callback_picked_genre(payload, event):
    sender_id = event.sender_id
    if payload == "PICK_SSH":
        page.send(sender_id,"Please Share your credentials \n ( format id: username hostname password ) ")      # TODO
    else:
        page.send(sender_id,"That's just fine")


@app.route('/authorize', methods=['GET'])
def authorize():
    account_linking_token = request.args.get('account_linking_token', '')
    redirect_uri = request.args.get('redirect_uri', '')

    auth_code = '1234567890'

    redirect_uri_success = redirect_uri + "&authorization_code=" + auth_code

    return render_template('authorize.html', data={
        'account_linking_token': account_linking_token,
        'redirect_uri': redirect_uri,
        'redirect_uri_success': redirect_uri_success
    })

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

def shell_commands(hostname,username,password,command):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    result = stdout.read()
    client.close()
    return result

def send_commands(from_path,remote_path,hostname,username,password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, username=username, password=password)
    try:
        sftp = client.open_sftp()
        debug(2)
        print(from_path,remote_path)
        sftp.get(from_path, remote_path)
        debug(3)
        return True
    except Exception as e:
        print(e)
        return False

# def shell_commands(hostname,username,password,command):
#     shell = spur.SshShell(hostname=hostname, username=username, password=password,missing_host_key=spur.ssh.MissingHostKey.accept)
#     with shell:
#         result = shell.run([command],allow_error=True)
#     print(result.output) # PARSE

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
    app.run(host='0.0.0.0', port=8080,debug=True,use_reloader=False)
