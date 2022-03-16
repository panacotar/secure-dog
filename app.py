import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session

# Configure application
app = Flask(__name__)

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

# CREATE TABLE users (
#   id INTEGER, 
#   email TEXT NOT NULL, 
#   username TEXT NOT NULL, 
#   profile_photo_url TEXT, 
#   Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
#   bio TEXT,
#   PRIMARY KEY(id)
# )