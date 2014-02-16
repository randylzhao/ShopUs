from flask import *
from flask.ext.pymongo import PyMongo
from dwolla import DwollaUser


import os
import json
import twilio.twiml

internet=True
app = Flask(__name__)
app.config['DEBUG']=True
PHONE = "412-515-8483"
app.secret_key = os.urandom(100)
if internet:
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
    if internet:
        db = mongo.db
        return str(db.posts.find_one({"User":"Rex"}))
    return "no internet, can't retrieve database"

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
        if internet:
            db = mongo.db
            if request.method=='POST':
                huntname = request.form['name']
                prize = float(request.form['prize'])
                keys = request.form.getlist('keys[]')
                clues = request.form.getlist('clues[]')
                email = session['user']
                reward = float(request.form['reward'])
                firmname = db.users.find_one({"Email":email})["Firm"]
                length = len(keys)
                db.hunts.insert({'huntname':huntname, 'prize':prize, 'reward':reward, 'keys':str(json.dumps(keys)), 'clues':str(json.dumps(clues)), 'Email':email, 'Firm': firmname, 'length':length })
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
        if internet:
            db = mongo.db
            username = request.form['signup_email']
            name = request.form['signup_firm']
            password = request.form['signup_password']
            key = request.form['signup_token']
            pin = request.form['signup_pin']
            if(db.users.find_one({"Email":username}) != None):
                flash("that username is already in use")
                return render_template('signup.html')
            else:
                if internet:
                    db.users.insert({"Email":username,"Password":password, "Firm": name, "token":key, "pin":pin})
            flash("signup successful")
            return redirect(url_for('adlogin'))
    else:
        return render_template('signup.html')

def login(name, password):
    if internet:
        db = mongo.db
        usr_obj = db.users.find_one({"Email":name})
    if( (usr_obj != None) and (usr_obj['Password']==password)):
        return True
    else:
        return False

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/viewhunts')
def customer():
    db = mongo.db
    hunts = db.hunts.find().sort("Firm")
    return render_template('viewhunts.html', hunts = hunts, phone = PHONE)


def format(unformated):
    nums = unformated[1:]
    one = "1"
    if len(nums) < 10: return "1-111-111-1111"
    if len(nums) == 11:
    	nums = unformated[1:]
    first = nums[:3]
    second = nums[3:6]
    third = nums[6:10]
    return one + "-" + first + "-" + second + "-" + third


@app.route("/founditem", methods=['GET', 'POST'])
def found_item():
    item = str(request.values.get('Body', None))
    number = format(request.values.get('From', None))
    
    message = ""
    if internet: 
        db = mongo.db
        number_obj = db.numbers.find_one({'Number': number})
    active_hunt = None
    if number_obj != None: 
        active_hunt = number_obj['activehunt']	
    
    #User starts a hunt
    if active_hunt == None:
    	#Checks whether 'item' (a hunt name) is a valid huntname
    	active_hunt = db.hunts.find_one({'huntname':item})
    	if active_hunt == None:
    	    #hunt is not valid
	    message = message + "Hunt ("+item+") not found."
	    resp = twilio.twiml.Response()
	    resp.message(message)
	    return str(resp)
	else:
            if internet:
                #hunt is valid, so add a number to numbers database
                db.numbers.insert({"Number": number, "activehunt": active_hunt, "cluenumber": 0})
                keys = active_hunt['keys']
                message = message + "You have registed for " + active_hunt['huntname'] + ". Find " + clues[0]
                resp = twilio.twiml.Response()
                #update participants
                participants = active_hunt['participants']
                db.hunts.update({'_id':active_hunt['_id']},{'$set':{'participants':participants+1}},upsert=False, multi=False)
                resp.message(message)
                return str(resp)	    
            else:
                return "no internet"
    #number is registered with a hunt
    user = db.numbers.find_one({'Number':number})
    keys = json.loads(active_hunt['keys'])
    index = user['cluenumber']    

    if item == keys[index]:
    	#Correct answer
    	index = index + 1
        message = "Congrats! You found " + item + ". "
        #update cluenumber
        db.numbers.update({'_id':user['_id']},{'$set':{'cluenumber':index}},upsert=False, multi=False)
        if index >= len(keys):
            #You're done. Remove number from database
            active_hunt = db.hunts.find_one({'huntname':user['activehunt']['huntname']})
            left = active_hunt['prizes']
            reward = active_hunt['reward']
            if left>=reward:
                db.numbers.update({'_id':active_hunt['_id']},{'$set':{'prizes':left-reward}},upsert=False, multi=False)
                person = db.users.find_one({'Email':active_hunt['Email']})
                DU = DwollaUser(person['token'])
                DU.send_funds(active_hunt['reward'], user['Number'], person['pin'])

                message = message + "Congratulations! You have won $("+active_hunt['reward']+")!"
                resp = twilio.twiml.Response()
                resp.message(message)
            else:
                message = message + "Congratulations! You have won. However, all the rewards have already been plundered. :'("
                resp = twilio.twiml.Response()
                resp.message(message)
                
            if internet:
                db.numbers.remove({'Number':number})
        else:
            message = message + "Now try to find " + keys[index]
            resp = twilio.twiml.Response()
            resp.message(message)    
    else:
        message = "Sorry (" + item+") is not the right answer."   
        resp = twilio.twiml.Response()
        resp.message(message)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
    



