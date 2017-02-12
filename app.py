import os
import sys
import json
import urllib2
import requests
from flask import Flask, request
from random import randint

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "code uploaded", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message
                
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]# the message's text
                    message_text= message_text.lower()
                    
                    if message_text == "news":
                        message_news(sender_id)
                        break;
                    if message_text=="help":
                        message_help(sender_id)
                        
                
                        break;
                    
                    
                    
                    if message_text=="add":
                        addurl()
                        break;
                                        
                    if message_text =="hey" or message_text=="hi" or message_text=="hello":
                        send_message(sender_id,"Hola!" )
                        break;
                    else:                                                       #catches query
                        send_message(sender_id,"Welcome to HolaBot")
                        send_message(sender_id,"Type 'help' in chat if you want to know what holabot responds to")
                        break;
                 
                            
                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["postback"]["payload"]# the message's text
                    message_text= message_text.lower()
                    
                    if message_text == "news":
                        message_news(sender_id)
                    if message_text =="hey" or message_text=="hi" or message_text=="hello":
                        send_message(sender_id,"Hola!" )







    return "ok", 200


def addurl():

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
                      "setting_type" : "domain_whitelisting",
                      "whitelisted_domains" : ["https://cdn0.vox-cdn.com"],
                      "domain_action_type": "add"
                      })
    r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings?", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)




def message_help(recipient_id):
    log("sending message to {recipient}".format(recipient=recipient_id))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
                      "recipient": {
                      "id": recipient_id
                      },
                      "message":{
                      "attachment":{
                      "type":"template",
                      "payload":{
                      "template_type":"button",
                      "text":"I can do the following stuff",
                      "buttons":[
                                 {
                                 "type":"postback",
                                 "title":"News",
                                 "payload":"news"
                                 },
                                 {
                                 "type":"postback",
                                 "title":"Hi",
                                 "payload":"hi"
                                 }
                                 ]
                      }
                      }
                      }
                      
                      })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)



def news(sender_id):
    j = urllib2.urlopen('https://newsapi.org/v1/articles?source=the-hindu&sortBy=top&apiKey=e40c47087f914323b5b4cf28b35d0fa9')
    j_obj =json.load(j)
    for i in range(5):
        temp= j_obj['articles'][i]['title'] #SENDING THE ARTICLES
        send_message(sender_id, temp)
        img=j_obj['articles'][i]['url'] #SENDING THE IMAGELINKS
        send_message(sender_id,img)
        break;

def message_news(recipient_id):
    url=randint(0,3)
    if url ==0:
        j = urllib2.urlopen('https://newsapi.org/v1/articles?source=engadget&sortBy=top&apiKey=e40c47087f914323b5b4cf28b35d0fa9')
    
    if url ==1:
        j= urllib2.urlopen(' https://newsapi.org/v1/articles?source=engadget&sortBy=latest&apiKey=e40c47087f914323b5b4cf28b35d0fa9')


    if url ==2:
        j= urllib2.urlopen(' https://newsapi.org/v1/articles?source=the-verge&sortBy=top&apiKey=e40c47087f914323b5b4cf28b35d0fa9')

    if url ==3:
        j= urllib2.urlopen('https://newsapi.org/v1/articles?source=the-verge&sortBy=latest&apiKey=e40c47087f914323b5b4cf28b35d0fa9')

    true = True
    i=randint(0,4)
    j_obj =json.load(j)
    log("sending message to {recipient}".format(recipient=recipient_id))
    
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
}
    headers = {
        "Content-Type": "application/json"
}
    data = json.dumps({
                      "recipient": {
                      "id": recipient_id
                      },
                      "message":{
                      "attachment":{
                      "type":"template",
                      "payload":{
                      "template_type":"generic",
                      "elements":[
                                  {
                                  "title":j_obj['articles'][i]['title'],
                                  "image_url":j_obj['articles'][i]['urlToImage'],
                                  "subtitle":j_obj['articles'][i]['description'],
                                  "default_action": {
                                  "type": "web_url",
                                  "url": j_obj['articles'][i]['url'],
                                  "messenger_extensions": true,
                                  "webview_height_ratio": "tall",
                                  "fallback_url": j_obj['articles'][i]['url']
                                  },
                                  "buttons":[
                                             {
                                             "type":"web_url",
                                             "url":j_obj['articles'][i]['url'],
                                             "title":"Go to Website"
                                             },{
                                             "type":"postback",
                                             "title":"Next article",
                                             "payload":"news"
                                             }              
                                             ]      
                                  }
                                  ]
                      }
                      }
                      }
                      })


    
 
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)




                        

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
