# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
from flask import redirect
import pprint
from flask import session, url_for
from datetime import datetime


# -- Initialization section --
app = Flask(__name__)

events = [
        {"event":"First Day of Classes", "date":"2019-08-21"},
        {"event":"Winter Break", "date":"2019-12-20"},
        {"event":"Finals Begin", "date":"2019-12-01"}
    ]

# name of database
app.config['MONGO_DBNAME'] = 'food-fusion'
# URI of database
app.config['MONGO_URI'] = 'mongodb+srv://admin:helloworld@cluster0.ovdqf.mongodb.net/food-fusion?retryWrites=true&w=majority'

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
    # need to store user import 
    if request.method == "GET":
        return render_template('donate.html', time=datetime.now())
    else:
        # this is storing the data from the form 
        name = request.form['name']
        city = request.form['city']
        description = request.form['description']
        typeoffood = request.form['type']
        email = request.form['email']
        # this is connecting to mongodb
        donate = mongo.db.donate
        # insert new data
        donate.insert({'name': name, 'city': city, 'description': description, 'type': typeoffood, 'email': email})
        # return a message to the user
        return "You added food to the database"

@app.route('/receive', methods = ["GET", "POST"])

def receive():
    # need to store user import 
    if request.method == "GET":
        return render_template('receive.html', time=datetime.now())
    else:
        # this is storing the data from the form 
        city = request.form['city']
        typeoffood = request.form['type']
        # this is connecting to mongodb
        donate = mongo.db.donate
        donateView = list(donate.find({'city': city, 'type': typeoffood})) # sort?
        print(donateView)
        return render_template('receive.html', time=datetime.now(), donateView=donateView)

        # return "You requested food"
    # connect to the database
    # insert new data