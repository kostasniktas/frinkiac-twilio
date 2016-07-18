import frinkiaccommands
import flask

app = flask.Flask(__name__)

@app.route("/")
def hello():
    return "Hey there"

@app.route("/random")
def random():
    return query("#random")

@app.route("/query/<querystr>")
def query(querystr):
    response = frinkiaccommands.do_stuff(querystr)
    return _basic_html(response)

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
