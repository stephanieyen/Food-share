# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo, ObjectId
from flask import redirect
from flask import session, url_for
from datetime import datetime
import pprint
import os

# -- Initialization section --
app = Flask(__name__)

user = os.environ["user"]
pw = os.environ["pw"]

# name of database
app.config['MONGO_DBNAME'] = 'food-fusion'
# URI of database
app.config['MONGO_URI'] = f'mongodb+srv://{user}:{pw}@cluster0.ovdqf.mongodb.net/food-fusion?retryWrites=true&w=majority'

mongo = PyMongo(app)

# -- Routes section --

# INDEX

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', time = datetime.now())


# CONNECT TO DB, ADD DATA

@app.route('/donate', methods = ["GET", "POST"])
def donate():
    if request.method == "GET":
        return render_template('donate.html', time=datetime.now())
    else:
        # store the data from the donate form so we can add it to mongodb
        name = request.form['name']
        city = request.form['city'].lower()
        description = request.form['description']
        typeoffood = request.form['type']
        email = request.form['email']
        quantity = request.form['quantity']
        # connect to the donate collection in mongodb
        donate = mongo.db.donate
        # insert new data to the donate collection
        donate.insert({'name': name, 'city': city, 'description': description, 'type': typeoffood, 'email': email, 'quantity': quantity})
        # display the Confirmation page
        return render_template('confirmation.html', time=datetime.now())

@app.route('/receive', methods = ["GET", "POST"])
def receive():
    if request.method == "GET":
        return render_template('receive.html', time=datetime.now())
    else:
        # store the data from the receive form so we can query it from mongodb
        name = request.form['name'] 
        city = request.form['city'].lower()
        typeoffood = request.form['type']
        email = request.form['email']
        # connect to the donate collection in mongodb
        donate = mongo.db.donate
        # show donated foods if it matches the receiver's city and type of food
        donateview = list(donate.find({'city': city, 'type': typeoffood}))
        sorted_donateview = sorted(donateview, key=lambda k: k['description']) # sort by description
        if len(donateview) > 0:
            # connect to the receive collection in mongodb
            receive = mongo.db.receive
            # insert new data to the receive collection
            receive_id = receive.insert({'name': name, 'city': city, 'type': typeoffood, 'email': email})
            # display success message and matching donations
            num_results = len(donateview)
            message = f"You got {num_results} results!"
            return render_template('receive.html', time=datetime.now(), donateview=sorted_donateview, message=message, receive_id=receive_id)
        else:
            # display failure message
            message = "Sorry, we couldn't find any results."
            return render_template('receive.html', time=datetime.now(), donateview=sorted_donateview, message=message)

@app.route('/check_availability/<id>/<receive_id>', methods = ["GET", "POST"])
# this route is accessed after the user clicks "See availability" on a certain donation on the Receive page
def check_availability(id, receive_id):
    if request.method == "GET":
        # connect to the donate collection in mongodb
        donate = mongo.db.donate
        # use donate ID to find the specific donation that the receiver clicks on
        identity = ObjectId(str(id))
        donateview = list(donate.find({"_id": identity}))
        # store the data from the donate form so we can display it 
        name = donateview[0]["name"]
        email = donateview[0]["email"]
        description = donateview[0]["description"]
        typeoffood = donateview[0]["type"]
        quantity = donateview[0]["quantity"]
        return render_template('check-availability.html', time=datetime.now(), name=name, email=email, description=description, typeoffood=typeoffood, quantity=quantity,
                                                          id=identity, receive_id=receive_id)

@app.route('/move_food/<id>/<receive_id>', methods = ["GET", "POST"])
# this route is accessed after the user clicks "Submit" on the Check Availability page
def move_food(id, receive_id):
    # connect to the donate collection in mongodb
    donate = mongo.db.donate
    # use donate ID to find the specific donation that the receiver clicks on
    identity = ObjectId(str(id))
    donateview = list(donate.find({"_id": identity}))
    # store the data from the donate form 
    name = donateview[0]["name"]
    email = donateview[0]["email"]
    description = donateview[0]["description"]
    typeoffood = donateview[0]["type"]
    quantity = donateview[0]["quantity"]
    if request.method == "GET":
        # display the Check Availability page
        return render_template('check-availability.html', time=datetime.now(), name=name, email=email, description=description, typeoffood=typeoffood, quantity=quantity,
                                                          id=identity, receive_id=receive_id)
    else:
        # use receive ID to add the receiver's requested quantity to their document in mongodb
        receive_identity = ObjectId(str(receive_id))
        user_quantity = request.form['quantity']
        # compare the receiver's requested quantity with the quantity that's already in the donate collection
        remaining_quantity = int(quantity) - int(user_quantity)
        if remaining_quantity >= 0: 
            # connect to the receive collection in mongodb
            receive = mongo.db.receive
            # update the receiver's document with their requested quantity
            receive.update({'_id': receive_identity}, {"$set": {'quantity': user_quantity}})
            # store the receiver's data so we can display it 
            searchreceive = list(receive.find({"_id": receive_identity}))
            receive_name = searchreceive[0]["name"]
            receive_email = searchreceive[0]["email"]
            receive_city = searchreceive[0]["city"]
            receive_type = searchreceive[0]["type"]
            receive_quantity = searchreceive[0]["quantity"]
            if remaining_quantity > 0:
                # if remaining quantity is > 0, update the document in the donate collection
                donate.update({'_id': identity}, {"$set": {'quantity': str(remaining_quantity)}})
                # display the Receive Confirmation page
                return render_template('receive-confirmation.html', time=datetime.now(), description=description, receive_name=receive_name, receive_email=receive_email, receive_city=receive_city, receive_type=receive_type, receive_quantity=receive_quantity)
            else:
                # if remaining quantity equals 0, remove the document from the donate collection
                donate.remove({"_id": identity})
                # display the Receive Confirmation page
                return render_template('receive-confirmation.html', time=datetime.now(), description=description, receive_name=receive_name, receive_email=receive_email, receive_city=receive_city, receive_type=receive_type, receive_quantity=receive_quantity)
        else:
            # if remaining quantity is < 0, show donate quantity
            donate_quantity = donateview[0]["quantity"]
            # display the Receive Failure page 
            return render_template('receive-fail.html', time=datetime.now(), donate_quantity = donate_quantity)

# TESTING

@app.route('/deleteall')
def deleteall():
    # receive collection
    receive = mongo.db.receive
    receiveview = receive.find({})
    receive.remove({})
    # donate collection
    donate = mongo.db.donate
    donateview = donate.find({})
    donate.remove({})
    # confirmation message
    return "You deleted everything"

@app.route('/deletereceive')
def deletereceive():
    # receive collection
    receive = mongo.db.receive
    receiveview = receive.find({})
    receive.remove({})
    # confirmation message
    return "You deleted everything in the receive collection"