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
        # this is storing the data from the form 
        name = request.form['name']
        city = request.form['city'].lower()
        # print(city)
        description = request.form['description']
        typeoffood = request.form['type']
        email = request.form['email']
        quantity = request.form['quantity']
        # this is connecting to mongodb
        donate = mongo.db.donate
        # insert new data
        donate.insert({'name': name, 'city': city, 'description': description, 'type': typeoffood, 'email': email, 'quantity': quantity})
        # return a message to the user
        return render_template('confirmation.html', time=datetime.now())
@app.route('/receive', methods = ["GET", "POST"])

def receive():
    if request.method == "GET":
        return render_template('receive.html', time=datetime.now())
    else:
        # this is storing the data from the form 
        name = request.form['name'] 
        city = request.form['city'].lower()
        # print(city)
        typeoffood = request.form['type']
        email = request.form['email']
        # this is connecting to mongodb
        donate = mongo.db.donate
        donateView = list(donate.find({'city': city, 'type': typeoffood})) # sort?
        if len(donateView) > 0:
            receive = mongo.db.receive
            receive_id = receive.insert({'name': name, 'city': city, 'type': typeoffood, 'email': email})
            # print(receive_id)
            message = "You got some results!"
            return render_template('receive.html', time=datetime.now(), donateView=donateView, message=message, receive_id = receive_id)
        else:
            message = "Sorry, we couldn't find any results."
            return render_template('receive.html', time=datetime.now(), donateView=donateView, message=message)
        # print(donateView)

@app.route('/deleteall')
def deleteall():
    receive = mongo.db.receive
    view = receive.find({})
    receive.remove({})
    donate = mongo.db.donate
    view2 = donate.find({})
    donate.remove({})
    return "You deleted everything"

@app.route('/check_availability/<id>/<receive_id>', methods = ["GET", "POST"])
def check_availability(id, receive_id):
    if request.method == "GET":
        # this is storing the data from the form
        donate = mongo.db.donate
        identity = ObjectId(str(id))
        # print(identity)
        donateview = list(donate.find({"_id": identity}))
        # print(donateview)
        quantity = donateview[0]["quantity"]
        food = donateview[0]["description"]
        kind = donateview[0]["type"]
        name = donateview[0]["name"]
        email = donateview[0]["email"]
        # print(quantity)
        return render_template('message.html', time=datetime.now(), quantity = quantity, food = food, kind = kind, name = name, email = email, id = identity, receive_id = receive_id)

@app.route('/move_food/<id>/<receive_id>', methods = ["GET", "POST"])
def move_food(id, receive_id):
    if request.method == "GET":
        donate = mongo.db.donate
        identity = ObjectId(str(id))
        # print(identity)
        donateview = list(donate.find({"_id": identity}))
        # print(donateview)
        quantity = donateview[0]["quantity"]
        food = donateview[0]["description"]
        kind = donateview[0]["type"]
        name = donateview[0]["name"]
        email = donateview[0]["email"]
        # print(quantity)
        return render_template('message.html', time=datetime.now(), quantity = quantity, food = food, kind = kind, name = name, email = email, id = identity, receive_id = receive_id)
    else:
        # get the user quantity from form
        user_quantity = request.form['quantity']
        # connect with database and query the database and store variables "89-98"
        donate = mongo.db.donate
        identity = ObjectId(str(id))
        receive_identity = ObjectId(str(receive_id))
        donateview = list(donate.find({"_id": identity}))
        quantity = donateview[0]["quantity"]
        kind = donateview[0]["type"]
        # subtraction = subtract user_quantity from quantity
        remaining = int(quantity) - int(user_quantity)
        # print(remaining)
        # compare it with the quantity that's already in the database
        if remaining > 0:
            # insert new data
            receive = mongo.db.receive
            # receive.insert({'quantity': quantity})
            receive.update({'_id': receive_identity}, {"$set": {'quantity': user_quantity}})
            searchreceive = list(receive.find({"_id": receive_identity}))
            receive_name = searchreceive[0]["name"]
            receive_city = searchreceive[0]["city"]
            receive_type = searchreceive[0]["type"]
            receive_email = searchreceive[0]["email"]
            receive_quantity = searchreceive[0]["quantity"]
            for item in searchreceive:
                print(item)
            donate.update({'_id': identity}, {"$set": {'quantity': str(remaining)}})
            # donate = mongo.db.donate
            donateview = list(donate.find({"_id": identity}))
            quantity = donateview[0]["quantity"]
            food = donateview[0]["description"]
            kind = donateview[0]["type"]
            name = donateview[0]["name"]
            email = donateview[0]["email"]
            message = "Here's a summary of your receive request: "
            return render_template('receive-confirmation.html', time=datetime.now(), quantity = quantity, food = food, kind = kind, name = name, email = email, identity = identity, 
                receive_name = receive_name, receive_city = receive_city, receive_type = receive_type, receive_email = receive_email, receive_quantity = receive_quantity, message=message)
        elif remaining == 0:
            # insert new data
            receive = mongo.db.receive
            receive.update({'_id': receive_identity}, {"$set": {'quantity': user_quantity}})
            searchreceive = list(receive.find({"_id": receive_identity}))
            receive_name = searchreceive[0]["name"]
            receive_city = searchreceive[0]["city"]
            receive_type = searchreceive[0]["type"]
            receive_email = searchreceive[0]["email"]
            receive_quantity = searchreceive[0]["quantity"]
            donate = mongo.db.donate
            donateview = list(donate.find({"_id": identity}))
            food = donateview[0]["description"]
            donate.remove({"_id": identity})
            message = "Here's a summary of your receive request: "
            return render_template('receive-confirmation.html', time=datetime.now(), food=food, receive_name = receive_name, receive_city = receive_city, receive_type = receive_type, receive_email = receive_email, receive_quantity = receive_quantity, message=message)
        else:
            # Show donate quantity
            donate = mongo.db.donate
            donateview = list(donate.find({"_id": identity}))
            donate_quantity = donateview[0]["quantity"]
            return render_template('receive-fail.html', time=datetime.now(), donate_quantity = donate_quantity)
        # if subtraction is negative then say "we don't have enough"
        # else do the subtraction and save it to the database
        # return "page in progress"
