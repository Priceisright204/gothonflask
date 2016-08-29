from flask import Flask, redirect, render_template, request, url_for, session
from simplekv.memory import DictStore

#the next two are just for creating a key for the server-side cookies.
import random
import string

#must use flask_kvsession because flask "session" does not support storing non-JSON objects (the map!).
from flask_kvsession import KVSessionExtension

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

count = 12

@app.route('/')
def index():
    session["room"] = map.START
    return redirect(url_for('game'))

@app.route('/game')
def game():
#    global session
    #if the user returned text
    if request.args.get('action'):
        action = request.args.get('action').lower()
        #if that text actually matches a path
        if session['room'].paths.get(action):
            session['room'] = session['room'].go(action)
            return redirect(url_for('game'))
        else:
            #if there's a special room that operates differently,
            #call the function for it and pass the text. (e.g. the ARMORY)
            if session['room'].status:
                return eval(session['room'].status) #I couldn't think of another way.
            else:   #if the text isn't recognized...
                session['room'].add_message("Error: I did not understand that.")
                return render_template("show_room.html", room=session["room"])
            return redirect(url_for('game'))
    else: #if no text was returned...
        if session["room"]:
            return render_template("show_room.html", room=session["room"])
        else:
            return redirect(url_for('index'))

            
@app.route('/armory')
def armory(string = None):
    #there SHOULD be a string passed.
    if string:
        #check if that string is an integer, and if it's in range.
        try:
            var = int(string)
            if var>999 or var<0:
                raise ValueError
        except ValueError:
            session['room'].add_message("Error: not a valid number!")
            return render_template("show_room.html", room=session["room"])

        #too much to type otherwise.
        code = int(session['room'].other_vars["code"])
        
        #I tried doing a variable in the class, but it would not update. This is easier.
        global count
        count -= 1
        if count == 0:
            count = 12
            session['room'] = session['room'].go("*")
            return render_template("show_room.html", room=session["room"])
        elif var < code:
            session['room'].add_message("Your guess is too low!    Guesses remaining: %s" % count )
            return render_template("show_room.html", room=session["room"])
        elif var > code:
            session['room'].add_message("Your guess is too high!    Guesses remaining: %s" % count)
            return render_template("show_room.html", room=session["room"])
        elif var == code:
            session['room'] = session['room'].go("13579")
            count = 12 #reset count variable, in case they play again.
            return redirect(url_for('game'))
    #if no string was passed
    else:
        session['room'].add_message("%d guesses remaining." % session['room'].other_vars["count"])
        return render_template("show_room.html", room=session["room"])



        
            
#Put "localhost" in the address bar.
if __name__ == "__main__":
    app.run( 
        host="0.0.0.0",
        port=int("80")
    )  #port 80 means you don't have to type :8080 in the address bar :-)
