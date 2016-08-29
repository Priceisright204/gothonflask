from flask import Flask, redirect, render_template, request, url_for, session
from simplekv.memory import DictStore

#must use flask_kvsession because flask "session" does not support storing non-JSON objects.
from flask_kvsession import KVSessionExtension

#the next two are just for creating a key for the server-side cookies.
import random
import string

#the "map" object
import map


app = Flask(__name__)
app.config.from_object(__name__)

#super secure cookies! You just try breaking that.
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for x in xrange(32))

#set up KVSession instance
store = DictStore()                         
KVSessionExtension(store, app)
    
@app.route('/')
def index():
    session["room"] = map.START
    return redirect(url_for('game'))

@app.route('/game')
def game():
    global session
    if request.args.get('action'):
        session['room'] = session['room'].go(request.args.get('action'))
        # And then redirect the user to the main page
        return redirect(url_for('game'))
    else:
        if session["room"]:
            return render_template("show_room.html", room=session["room"])
        else:
            return render_template('you_died.html')

#Put "localhost" in the address bar.
if __name__ == "__main__":
    app.run( 
        host="0.0.0.0",
        port=int("80")
    )  #port 80 means you don't have to type :8080 in the address bar :-)
