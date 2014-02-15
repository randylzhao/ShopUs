import os
from flask import Flask, url_for, render_template, request,flash
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.secret_key = os.urandom(100)
if not hasattr(app.config,'MONGO_URI'):
    app.config['MONGO_URI'] = 'mongodb://heroku_app22228003:nnk0noj15se1nk9bfjf5ofo165@ds027769.mongolab.com:27769/heroku_app22228003'
mongo = PyMongo(app)
@app.route('/')
def hello():
    return "Hello World"

@app.route('/retrieve')
def retrieve():
    db = mongo.db
    return str(db.posts.find_one({"User":"Rex"}))

@app.route('/login', methods = ['GET', 'POST'])
def advertiserhome():
    if request.method == 'POST':
        username = request.form['login_email']
        password = request.form['login_password']
        login(username, password)
    else:
        return render_template('login.html')

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
            flash("signup successful")
            return render_template('signup.html')
    else:
        return render_template('signup.html')

def login(name, password):
        db = mongo.db
        usr_obj = db.users.find_one({"User":name})
        if( (usb_obj != None) and (usb_obj['password']==password)):
            return render_template('login_success.html')

@app.route('/user')
def user():
    retrieve()

@app.route('/insert')
def upd():
    db = mongo.db
    db.posts.insert({"User": "Rex", "Role": "Test"})
    return 'Success'

app.run(debug=True)
