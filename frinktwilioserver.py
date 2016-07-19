import frinkiaccommands
import flask
import twilio.twiml
import cgi

app = flask.Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def hello():
    print str(flask.request.values)
    return str(query(flask.request.values.get("Body"), tml=True))

@app.route("/random")
def random():
    return query("#random")

@app.route("/t/random")
def trandom():
    return "<pre>{}</pre>".format(cgi.escape(query("#random", tml=True)))

@app.route("/t/query/<querystr>")
def tquery(querystr):
    return "<pre>{}</pre>".format(cgi.escape(query(querystr, tml=True)))

@app.route("/query/<querystr>")
def query(querystr, tml = False):
    response = frinkiaccommands.do_stuff(querystr)
    if tml:
        return _twiml(response)
    return _basic_html(response)

def _twiml(frame):
    response = twilio.twiml.Response()
    if (frame["imageurl"] is not None):
        with response.message(frame["message"]) as m:
            m.media(frame["imageurl"])
    else:
        response.message(frame["message"])
    return str(response)

def _basic_html(frame):
    if not frame["error"]:
            return """<html><body>
<img src='{}'/><br/>
<h3>{}</h3>
</body></html>""".format(frame["imageurl"], frame["message"])
    else:
        return """<h3>There was an error:</h3><br/><bold>{}</bold>""".format(frame["message"])

if __name__ == "__main__":
    app.run()
