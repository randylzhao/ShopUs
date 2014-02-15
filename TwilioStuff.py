from flask import Flask, request, redirect
import twilio.twiml

hunt_list = [
    "cat",
    "dog",
    "1234"
]

@app.route("/founditem", methods=['GET', 'POST'])
def found_item():
    item = request.values.get('Body', None)
    number = request.values.get('From', None)
    
    db = Mongo.db
    active_hunt = db.numbers.find_one({'activehunt':number})
    
    #User starts a hunt
    if active_hunt == None:
    	#Checks whether 'item' (a hunt name) is a valid huntname
    	active_hunt = db.hunts.find_one({'huntname':item})
    	if active_hunt == None:
    	    #hunt is not valid
	    message = "No scavhunt found lolz"
	    resp = twilio.twiml.Response()
	    resp.message(message)
	    return str(resp)
	else
            #hunt is valid, so add a number to numbers database
	    db.numbers.insert({"Number": number, "activehunt": active_hunt, "cluenumber": 0})
	    keys = active_hunt['keys']
	    message = "Lolz. You registed for " + active_hunt['huntname'] + ". Find " keys[0]
	    resp = twilio.twiml.Response()
	    resp.message(message)
	    return str(resp)	    
        
    #number is registered with a hunt
    user = db.numbers.find_one({'number':number})
    keys = active_hunt['keys']
    index = user['cluenumber']    
    
    if item == keys[index]:
    	#Correct answer
    	index = index + 1
        message = "Congrats! You found " + item
        resp = twilio.twiml.Response()
        resp.message(message)
        #update cluenumber
        db.numbers.update({'number':number},{'cluenumber': index}, multi = True)
        
        if index >= len(keys):
            #You're done. Remove number from database
            message = "Lolz! You won! Congrats you scrub!"
            resp = twilio.twiml.Response()
            resp.message(message)
            db.numbers.remove({'number':number})
        else:
            message = "Now try to find " + keys[index]
            resp = twilio.twiml.Response()
            resp.message(message)    
    else:
        message = "Lolz. ur a n00b" + item   
        resp = twilio.twiml.Response()
        resp.message(message)
    return str(resp)
    

