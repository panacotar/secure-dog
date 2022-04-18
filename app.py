from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv() 

import json
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, \
  get_flashed_messages
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from validator_collection import errors as validator_errors

from utils.helpers import get_confirmation_code, get_expiration_date_milliseconds, mail_confirmation_code, \
  get_time_now_ms, check_email, check_url, validate_password, mail_analytics

from utils.decorators import login_required, unauthenticated_route

# Configure application
app = Flask(__name__)

# Configure Falsk Mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

# Initiate mail from Flask Mail
mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///dog.db")
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

@app.route("/", methods=["GET", "POST"])
@unauthenticated_route
def index():
  return render_template("index.html")

@app.route("/about", methods=["GET"])
def about():
  return render_template("about.html")

@app.route("/feed", methods=["GET", "POST"])
@login_required
def feed():
  """Show posts and create new post"""
  res = db.execute("SELECT * FROM posts ORDER BY created_at DESC;")

  if request.method == "POST":
    # Check if an logged user
    logged_user_id = session["user_id"]
    if not logged_user_id:
      flash("User not logged in")
      return redirect(request.url)

    # Validate Data
    # Check if URL missing
    url = request.form.get("url")
    description = request.form.get("description")
    if not url:
      flash("URL is missing")
      return render_template("feed.html", description=description, posts=res)
    
    # Check if URL is valid
    try:
      valid_url = check_url(url)
    except validator_errors.InvalidURLError:
      flash("URL not valid")
      return render_template("feed.html", url=url, description=description, posts=res)

    # Get the current user
    res_db = db.execute("SELECT username FROM users WHERE id = ?;", logged_user_id)

    # Error if not found user
    if len(res_db) != 1:
      flash("Author user not existing in the DB")
      return render_template("feed.html", url=url, description=description, posts=res)
    

    found_user = res_db[0]

    # Save the post in the DB
    res = db.execute("INSERT INTO posts (author_id, author_username, photo_URL, description) VALUES (?, ?, ?, ?)",
        logged_user_id,
        found_user["username"],
        valid_url,
        description
    )

    mail_analytics(mail, description)

    # Redirect user to /feed
    return redirect(request.url)

  return render_template("feed.html", posts=res)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
  """Register user"""
  if request.method == "POST":    
    email = request.form.get("email")
    username = request.form.get("username")

    # Track the user email in the session
    session["user_email"] = email
  
    # Validate presence of data
    if not email:
      flash("Email missing")
      # return redirect(request.url)
      return redirect(request.url)
      # return render_template("register.html", username=username)

    print(email)
    # Check if email is valid
    if not check_email(email):
      flash("Not a valid email")
      return redirect(request.url)
      # return render_template("register.html", email=email, username=username)

    if not username:
      flash("Username missing", "warning")
      return render_template("register.html", email=email)


    if not request.form.get("password"):
      flash("Password missing", "warning")
      return redirect(request.url)
      # return render_template("register.html", email=email, username=username)

    # Validate password
    try:
      validate_password(request.form.get("password"))
    except ValueError as error:
      print(f"error {error}")
      flash("Password must contain at least 6 characters, including lower/uppercase characters")
      return redirect(request.url)
      # return render_template("register.html", email=email, username=username)

    if request.form.get("password") != request.form.get("confirmation"):
      flash("Passwords do not match", "warning")
      return redirect(request.url)
      # return render_template("register.html", email=email, username=username)
    
    # Check if email exists already
    response = db.execute("SELECT * FROM users WHERE email = ?", email)

    if len(response):
      flash("User already exists, login with this email or choose another one", "warning")
      return redirect(request.url)
      # return render_template("register.html", email=email, username=username)

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

    # Track user email to the session
    session["user_email"] = email

    flash("Account created", "success")

    # Move user to /confirm
    return redirect("/confirm")

  return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  """Log user in"""
  msg = get_flashed_messages()

  # Forget any user_id
  # session.clear()
  
  if request.method == "POST":
    #Clear flash messages
    session.pop('_flashes', None)

    # Validate presence of data
    email = request.form.get("email")

    # Track the user email in the session
    session["user_email"] = email

    if not email:
      flash("Email missing", "warning")
      return redirect(request.url)

    if not request.form.get("password"):
      flash("Password missing", "warning")
      return redirect(request.url)
    
    # Check if user exists in the DB
    res = db.execute("SELECT * FROM users WHERE email = ?", email)
    if len(res) != 1 or not check_password_hash(res[0]["hash"], request.form.get("password")):
      flash("Email or password invalid", "warning")
      return redirect(request.url)
    
    user = res[0]
    # Check the hash password
    
    # Generate confirmation code
    confirmation_code = get_confirmation_code()

    # Get expiration date
    code_expiration = get_expiration_date_milliseconds()

    token_data = [confirmation_code, code_expiration]
    sql_token = json.dumps(token_data)
    # Save the token in the DB
    db.execute(
      "UPDATE users SET token=? WHERE id = ?",
        sql_token,
        user["id"]
    )

    # Send the confirmation code by email
    mail_confirmation_code(mail, email, confirmation_code)

    # Track user email to the session
    # session["user_email"] = user["email"]

    # Move user to /confirm
    return redirect("/confirm")

  return render_template("login.html")

@app.route("/confirm", methods=["GET", "POST"])
def confirm():
  if request.method == "POST":
  
    # Validate existence of confirmation code
    code = request.form.get("confirm-code")
    email = request.form.get("email")
    if not code:
      flash("Code missing")
      return render_template("confirm.html", email=email)
    
    # Fetch user
    res = db.execute("SELECT * FROM users WHERE email = ?", email)

    # Check if user exists
    if not len(res):
      flash("A user with this email does not exist")
      return redirect("/login")

    user = res[0]

    # Check if user has an active token
    if not user["token"]:
      flash("User does not have an active token")
      return redirect("/login")

    # Load the token json
    token = json.loads(user['token'])
    confirm_code = token[0]
    code_expiration = token[1]

    # Remove the confirmation code form the DB
    db.execute("UPDATE users SET token=NULL WHERE id = ?", user["id"])

    # Check if token is expired
    if get_time_now_ms() > code_expiration:
      flash("Sorry, the token has expired")
      return redirect("/login")
    
    # Check if token code is the same as the submitted code
    if code != confirm_code:
      flash("Sorry, the confirmation code is wrong")
      return redirect("/login")

    # If not confirmed, update the confirmed column of the user
    if not user["confirmed"]:
      db.execute("UPDATE users SET confirmed=1 WHERE id = ?", user["id"])

    # Add user to the session
    session["user_id"] = user["id"]

    # Untrack user_email from session
    session.pop("user_email")

    # Move user to the homepage
    return redirect("/feed")
  
  # Get user email from the session
  user_email = session["user_email"]

  print(f"USer email in session {user_email}")

  return render_template("confirm.html")

# ERROR HANDLING

# 404 - Not Found
@app.errorhandler(404)
def notFound(e):
  return render_template("errors/404.html")

# 500 - Internal Server Error
@app.errorhandler(500)
def notFound(e):
  return render_template("errors/500.html")

# 403 - Forbidden
@app.errorhandler(403)
def notFound(e):
  return render_template("errors/403.html")

# 405 - Method Not Allowed
@app.errorhandler(405)
def notFound(e):
  return render_template("errors/405.html")

if __name__ == '__main__':
   app.run(debug = True)