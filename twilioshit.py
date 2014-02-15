from flask import Flask, request, redirect
import twilio.twinl

hunt_list = [
    "cat",
    "dog",
    "1234"
]

@app.route("/founditem", methods=['GET', 'POST'])
def found_item():
    item = request.values.get('body', None)
    if item in hunt_list:
        message = "Congrats! You found " + item
    else:
        message = "Lolz. ur a n00b"
    
    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)
