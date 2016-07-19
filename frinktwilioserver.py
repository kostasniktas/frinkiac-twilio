import cgi
from flask import Flask, request
import frinkiaccommands
import logging
import twilio.twiml

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.route("/smsinbound", methods=["GET", "POST"])
def sms_inbound():
    message_id = request.values.get("SmsMessageSid")
    from_number = request.values.get("From")
    message_body = request.values.get("Body")

    logger.info(u"SMSReceived ID[{}] From[{}] Body[{}]".format(message_id, from_number, message_body))
    twiml = _query(message_body, tml=True, mid=message_id)
    return twiml

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
def random():
    return _query("#random")

@app.route("/randomnocaption")
def random_nocaption():
    return _query("#random #nocaption")

# Perform a query
def _query(querystr, tml=False, mid=None):
    frame = frinkiaccommands.do_stuff(querystr)
    if tml:
        response = _twiml(frame)
    else:
        response = _basic_html(frame)
    logger.info(u"Query ID[{}] TML[{}] Reponse[{}]".format(mid, tml, response))
    return response

# Format a frame into a TwiML
def _twiml(frame):
    response = twilio.twiml.Response()
    if (frame["imageurl"] is not None):
        with response.message(frame["message"]) as m:
            m.media(frame["imageurl"])
    else:
        response.message(frame["message"])
    return str(response)

# Format a frame with HTML
def _basic_html(frame):
    if not frame["error"]:
            return """<html><body>
<img src='{}'/><br/>
<h3>{}</h3>
</body></html>""".format(frame["imageurl"], frame["message"].replace("\n","</h3><h3>"))
    else:
        return """<h3>There was an error or info:</h3><br/><bold><pre>{}</pre></bold>""".format(frame["message"])


# RUN THE SERVER!!!
if __name__ == "__main__":
    app.run()
