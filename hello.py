import os
from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://heroku_app22228003:nnk0noj15se1nk9bfjf5ofo165@ds027769.mongolab.com:27769/heroku_app22228003'
mongo = PyMongo(app)

@app.route('/')
def hello():
    return "Hello WOrld"

@app.route('/retrieve')
def retrieve():
    db = mongo.db
    return str(db.posts.find_one({"User":"Rex"}))

@app.route('/insert')
def upd():
    db = mongo.db
    db.posts.insert({"User": "Rex", "Role": "Test"})
    return 'Success'
