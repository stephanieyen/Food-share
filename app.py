# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
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
        print(city)
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
        receive = mongo.db.receive
        # this is connecting to mongodb
        donate = mongo.db.donate
        donateView = list(donate.find({'city': city, 'type': typeoffood})) # sort?
        if len(donateView) > 0:
            receive.insert({'name': name, 'city': city, 'type': typeoffood, 'email': email})
            message = "You got some results!"
        else:
            message = "Sorry, we couldn't find any results."
        print(donateView)
        return render_template('receive.html', time=datetime.now(), donateView=donateView, message=message)

# @app.route('/deleteall')
# def deleteall():
#     donate = mongo.db.donate
#     view = donate.find({})
#     donate.remove({})
#     return "You deleted everything"

@app.route('/check_availability/<description>', methods = ["GET", "POST"])
def check_availability(description):
    if request.method == "GET":
        # this is storing the data from the form
        donate = mongo.db.donate
        donateview = list(donate.find({"description": description}))
        print(donateview)
        quantity = donateview[0]["quantity"]
        food = donateview[0]["description"]
        kind = donateview[0]["type"]
        name = donateview[0]["name"]
        email = donateview[0]["email"]
        print(quantity)
        return render_template('message.html', time=datetime.now(), quantity = quantity, food = food, kind = kind, name = name, email = email)
    else:
        # get the user quantity from form
        user_quantity = request.form['quantity']
        # connect with database and query the database and store variables "89-98"
        donate = mongo.db.donate
        donateview = list(donate.find({"description": description}))
        # print(donateview)
        quantity = donateview[0]["quantity"]
        kind = donateview[0]["type"]
        # print(quantity)
        # subtraction = subtract user_quantity from quantity
        remaining = int(quantity) - int(user_quantity)
        print(remaining)
        # compare it with the quantity that's already in the database
        if remaining > 0:
            # insert new data
            receive = mongo.db.receive
            searchreceive = list(receive.find({"type": kind}))
            receive.insert({'quantity': quantity})
            donate.update({'description': description}, {"$set": {'quantity': str(remaining)}})
            donate = mongo.db.donate
            donateview = list(donate.find({"description": description}))
            print(donateview)
            quantity = donateview[0]["quantity"]
            food = donateview[0]["description"]
            kind = donateview[0]["type"]
            name = donateview[0]["name"]
            email = donateview[0]["email"]
            print(quantity)
            return render_template('message.html', time=datetime.now(), quantity = quantity, food = food, kind = kind, name = name, email = email)
        elif remaining == 0:
            # insert new data
            receive.insert({'quantity': quantity})
            donate = mongo.db.donate
            donate.remove({"description": description})
            return render_template('receive.html', time=datetime.now())
        else: 
            return "You need more than we have available"
        # if subtraction is negative then say "we don't have enough"
        # else do the subtraction and save it to the database
        # return "page in progress"
