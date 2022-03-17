import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message

# Configure application
app = Flask(__name__, instance_relative_config=True)

# Configure Falsk Mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config.from_pyfile('config.py')

# Initiate mail from Flask Mail
mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///dog.db")

@app.route("/", methods=["GET", "POST"])
def index():
  return render_template("index.html")

@app.route("/mailing/<mail_address>")
def mailing(mail_address):
   """Send a template mail"""
   msg = Message('Hello', sender = 'securedog@gmail.com', recipients = [str(mail_address)])
   msg.body = "Secure dog email"
   mail.send(msg)
   return "Sent"
