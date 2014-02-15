from flask import *
from flask.ext.pymongo import PyMongo
import os
import json
import twilio.twiml


app = Flask(__name__)
PHONE = 4125158483
app.secret_key = os.urandom(100)
if not hasattr(app.config,'MONGO_URI'):
    app.config['MONGO_URI'] = 'mongodb://heroku_app22228003:nnk0noj15se1nk9bfjf5ofo165@ds027769.mongolab.com:27769/heroku_app22228003'
mongo = PyMongo(app)

'''
adhome.html - homepage which displays what hunts a firm has
signup.html - register account for advertisers
login.html - login for advertisers
createhunt.html - creates a scavenger hunt for advertisers
home.html - index page with two buttons one for customers and one for advertisers
viewhunts.html - displays the hunts available for customers
'''


@app.route('/')
def index():
    return render_template("home.html")

@app.route('/retrieve')
def retrieve():
    db = mongo.db
    return str(db.posts.find_one({"User":"Rex"}))

def loggedin():
    if 'user' in session:
        return True
    else:
        return False

@app.route('/createhunt')
def createhunt():
    if loggedin():
        return render_template('createhunt.html')
    else:
        return redirect(url_for('adlogin'))

@app.route('/addhunt', methods = ['POST'])
def addhunt():
    if loggedin():
        db = mongo.db
        if request.method=='POST':
            huntname = request.form['name']
            prize = float(request.form['prize'])
            keys = request.form['keys']
            email = session['user']
            firmname = db.users.find_one({"Email":email})["Firm"]
            db.hunts.insert({'huntname':huntname, 'prize':prize, 'keys':str(json.dumps(keys)), 'Email':email, 'Firm': firmname })
        return redirect(url_for('adhome'))
    else:
        return redirect(url_for('adlogin'))

@app.route('/adhome')    
def adhome():
    if loggedin():
        db = mongo.db
        myhunts = db.hunts.find({'Email':session['user']})
        return render_template('adhome.html',  hunts = myhunts)
    else:
        return redirect(url_for('adlogin'))

@app.route('/login', methods = ['GET', 'POST'])
def adlogin():
    if request.method == 'POST':
        username = request.form['login_email']
        password = request.form['login_password']
        if not (username in session):
            if login(username, password):
                session['user'] = username
                return redirect(url_for('adhome'))
            else:
                flash("could not log you in, either your \
                        email or password is wrong")
                return render_template('login.html')
        else:
            return redirect(url_for('adhome'))
    else:
        return render_template('login.html')

# since it's proof of concept we're not salting and bcrypting
@app.route('/signup', methods = ['GET','POST'])
def add_advertiser():
    if request.method == 'POST':
        db = mongo.db
        username = request.form['signup_email']
        name = request.form['signup_firm']
        password = request.form['signup_password']
        if(db.users.find_one({"Email":username}) != None):
            flash("that username is already in use")
            return render_template('signup.html')
        else:
            db.users.insert({"Email":username,"Password":password, "Firm": name})
            flash("signup successful")
            return redirect(url_for('adlogin'))
    else:
        return render_template('signup.html')

def login(name, password):
    db = mongo.db
    usr_obj = db.users.find_one({"Email":name})
    if( (usr_obj != None) and (usr_obj['Password']==password)):
        return True
    else:
        return False

def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/customer')
def customer():
    db = mongo.db
    hunts = db.hunts.find()
    return render_template('viewhunts.html', hunts = hunts, phone = PHONE)
        

if __name__ == "__main__":
    app.run(debug=True)



#Twilio shit
hunt_list = [
    "cat",
    "dog",
    "1234"
]

@app.route("/founditem", methods=['GET', 'POST'])
def found_item():
    item = request.values.get('Body', None)
    if item in hunt_list:
        message = "Congrats! You found " + item
    else:
        message = "Lolz. ur a n00b" + item
    
    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)
