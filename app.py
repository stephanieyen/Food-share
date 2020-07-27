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
    if request.method == "GET":
        return render_template('receive.html', time=datetime.now())
    else:
        # this is storing the data from the form 
        city = request.form['city']
        typeoffood = request.form['type']
        # this is connecting to mongodb
        donate = mongo.db.donate
        donateView = list(donate.find({'city': city, 'type': typeoffood})) # sort?
        if len(donateView) > 0:
            message = "You got some results!"
        else:
            message = "Sorry, we couldn't find any results."
        print(donateView)
        return render_template('receive.html', time=datetime.now(), donateView=donateView, message=message)

