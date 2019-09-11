import cgi
from flask import Flask, request, send_file
import frinkcommands
import logging
import os
import random
import re
import simpsonsvoice
import sys
import twilio.twiml
import twilio.rest

app = Flask(__name__)

logger = logging.getLogger('frinkiacsms')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler('frinkiacsms.log', maxBytes=100 * 1024**2)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# Call if necessary
SID = os.environ.get("ACCOUNT_SID")
TOK = os.environ.get("ACCOUNT_TOK")


@app.route("/sounds/<soundfile>", methods=["GET"])
def sounds_byebye(soundfile):
    if soundfile in simpsonsvoice.SIMPSONS_ALL_SOUNDS:
        return send_file('sounds/{}'.format(soundfile))
    return 'Could you explain the thing you were saying?', 404


@app.route("/smsinbound", methods=["GET", "POST"])
def sms_inbound():
    message_id = request.values.get("SmsMessageSid")
    from_number = request.values.get("From")
    message_body = request.values.get("Body")

    logger.info(u"SMSReceived ID[{}] From[{}] Body[{}]".format(message_id, from_number, message_body))
    twiml = _query(message_body, tml=True, mid=message_id)
    return twiml


@app.route("/voiceinbound", methods=["GET", "POST"])
def voice_inbound():
    response = twilio.twiml.Response()
    response.pause(length=2)
    response.say("I'm sorry.  The fingers you have used to dial, are too fat.", voice="alice")
    g = response.gather(timeout=7, numDigits=5, method="GET", action=request.url_root+"voiceinbound_choice")
    g.say("To obtain a special dialing wand please mash the keypad now.", voice="alice")
    response.say("No keys were pressed.", voice="alice", language="en-gb")
    response.play(request.host_url + 'sounds/' + simpsonsvoice.SIMPSONS_GOODBYE)
    response.hangup()
    return str(response)


@app.route("/voiceinbound_choice", methods=["GET"])
def voice_inbound_choice():
    response = twilio.twiml.Response()
    digits = request.values.get("Digits")
    digits = int(re.sub("[^0-9]", "", digits))
    choice = digits % len(simpsonsvoice.SIMPSONS_CLIPS)
    response.play(request.host_url + 'sounds/' + simpsonsvoice.SIMPSONS_CLIPS[choice])
    response.pause(length=1)
    response.hangup()
    return str(response)


@app.route("/voiceoutbound_random", methods=["GET", "POST"])
def voice_outbound_random():
    response = twilio.twiml.Response()
    response.pause(length=1)
    response.play(request.host_url + 'sounds/' + random.choice(simpsonsvoice.SIMPSONS_CLIPS))
    response.pause(length=1)
    response.hangup()
    return str(response)


@app.route("/")
def hello():
    return "It's Frinkiac SMS!"


@app.route("/searchdebug", methods=["GET"])
def search():
    return """<html>
    <head><title>Search Frinkiac SMS</title></head>
    <body>
        <form action="/searchdebug" method="POST">
            <input type="text" size=50 name="Body"/><br/>
            <label><input type="checkbox" value="TML" name="DebugTML"/>TwiML</label><br/>
            <input type="submit"/>
        </form>
    </body>
</html>"""


@app.route("/searchdebug", methods=["POST"])
def search_result():
    message_id = "WEBMESSAGE"
    from_number = "THEINTERWEBZ"
    message_body = request.values.get("Body")
    tml_check = request.values.get("DebugTML")
    logger.info(u"WebSMSReceived ID[{}] From[{}] Body[{}]".format(message_id, from_number, message_body))

    if tml_check and tml_check == "TML":
        search_response = u"<pre>{}</pre>".format(_query(message_body, tml=True, mid=message_id))
    else:
        search_response = _query(message_body)

    return search_response


@app.route("/random")
def random_query():
    return _query("#random")


@app.route("/randomnocaption")
def random_query_nocaption():
    return _query("#random #nocaption")

# Perform a query


def _query(querystr, tml=False, mid=None):
    frame = frinkcommands.do_stuff(querystr)
    if tml:
        response = _twiml(frame)
    else:
        response = _basic_html(frame)
    logger.info(u"Query ID[{}] TML[{}] Reponse[{}]".format(mid, tml, response).encode('utf8'))
    return response

# Format a frame into a TwiML


def _twiml(frame):
    response = twilio.twiml.Response()
    if (frame["callme"]):
        if SID is None or TOK is None:
            return str(twilio.twiml.Response())
        client = twilio.rest.TwilioRestClient(SID, TOK)
        client.calls.create(to=request.values.get("From"), from_=request.values.get("To"),
                            url=request.url_root+"voiceoutbound_random")
        return str(twilio.twiml.Response())
    if (frame["imageurl"] is not None):
        with response.message(frame["message"]) as m:
            m.media(frame["imageurl"])
    else:
        response.message(frame["message"])
    return str(response)

# Format a frame with HTML


def _basic_html(frame):
    if (frame["callme"]):
        sound = random.choice(simpsonsvoice.SIMPSONS_CLIPS)
        return """<html><body><a href="{}">sound</a></body></html""".format(sound)
    if not frame["error"]:
        return """<html><body>
<img src='{}'/><br/>
<h3>{}</h3>
</body></html>""".format(frame["imageurl"], frame["message"].replace("\n", "</h3><h3>").encode('utf8'))
    else:
        return """<h3>There was an error or info:</h3><br/><bold><pre>{}</pre></bold>""".format(frame["message"])


# RUN THE SERVER!!!
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
