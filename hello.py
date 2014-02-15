from flask import *
from flask.ext.pymongo import PyMongo
import os
import json

app = Flask(__name__)

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
        return render_template('createhunt.html', user=sesion['user'])
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
            db.hunts.insert({'huntname':huntname, 'prize':prize, 'keys':json.dumps(keys)})
        return redirect(url_for('adhome'))
    else:
        return redirect(url_for('adlogin'))

@app.route('/adhome')    
def adhome():
    if loggedin():
        db = mongo.db
        myhunts = db.hunts.find({'user':session['user']})
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
        password = request.form['signup_password']
        if(db.users.find_one({"User":username}) != None):
            flash("that username is already in use")
            return render_template('signup.html')
        else:
            db.users.insert({"Email":username,"Password":password})
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

@app.route('/user')
def user():
    db = mongo.db
    
    retrieve()

@app.route('/insert')
def upd():
    db = mongo.db
    db.posts.insert({"User": "Rex", "Role": "Test"})
    return 'Success'
if __name__ == "__main__":
    app.run(debug=True)
