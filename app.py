import os

import json

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_confirmation_code, get_expiration_date_milliseconds, mail_confirmation_code, \
  get_time_now_ms

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
  confirm_code = get_confirmation_code()
  return render_template("index.html", confirm_code=confirm_code)

@app.route("/register", methods=["GET", "POST"])
def register():
  """Register user"""
  if request.method == "POST":
    email = request.form.get("email")
    username = request.form.get("username")
    # Validate presence of data
    if not email:
      flash("Email missing")
      return render_template("register.html")
    if not username:
      flash("Username missing")
      return render_template("register.html")
    if not request.form.get("password"):
      flash("Password missing")
      return render_template("register.html")
    if request.form.get("password") != request.form.get("confirmation"):
      flash("Passwords do not match")
      return render_template("register.html")
    
    # Check if email exists already
    existing = db.execute("SELECT * FROM users WHERE email = ?", email)
    if existing:
      flash("User already exists, login with this email or choose another one")
      return render_template("register.html")

    # Generate a hash password
    hash_password = generate_password_hash(request.form.get("password"))
    
    # Generate confirmation code
    confirmation_code = get_confirmation_code()

    # Get expiration date
    code_expiration = get_expiration_date_milliseconds()

    token_data = [confirmation_code, code_expiration]
    sql_token = json.dumps(token_data)
    # Save user in the DB
    user = db.execute(
      "INSERT INTO users (email, username, hash, token) VALUES(?, ?, ?, ?)",
        email,
        username,
        hash_password,
        sql_token
      )
    
    print(f"new user in db: {user}")
    # Send the confirmation code by email
    mail_confirmation_code(mail, email, confirmation_code)
    # Move user to /confirm
    return redirect("confirm.html", email=email)
  return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  """Log user in"""

  # Forget any user_id
  session.clear()

  return render_template("login.html")


@app.route("/mailing/<mail_address>")
def mailing(mail_address):
   """Send a template mail"""
   msg = Message('Hello', sender = 'securedog@gmail.com', recipients = [str(mail_address)])
   msg.body = "Secure dog email"
   mail.send(msg)
   return "Sent"


if __name__ == '__main__':
   app.run(debug = True)