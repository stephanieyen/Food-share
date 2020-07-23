# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
from flask import redirect
import pprint
from flask import session, url_for


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
        return render_template('donate.html')
    else:
        # this is storing the data from the form 
        name = request.form['name']
        description = request.form['description']
        kind = request.form['type']
        email = request.form['email']
        city = request.form['city']
        # this is connecting events to mongodb
        donate = mongo.db.donate
        donate.insert({'name': name, 'description': description, 'type': kind, 'email': email, 'city': city})
        return "You added food to the database"
    # connect to the database
    # insert new data

    # return a message to the user
