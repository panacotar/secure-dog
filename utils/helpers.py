from random import randint
import re
import time
from flask import render_template
from validator_collection import validators, checkers

from flask_mail import Message

email_regex = '^[a-z0-9]+[\._]?[a-z0-9\+\S]+[@]\w+[.]\w{2,3}$'  

def get_confirmation_code():
  code = ""
  random_chars = [randint(0, 9) for _ in range(6)]
  return code.join(str(x) for x in random_chars)

def get_time_now_ms():
  return int(time.time()) * 1000

def get_expiration_date_milliseconds():
  # Get 15 mins in ms
  unix_15 = 900000
  # Get time now in ms
  time_now_ms = get_time_now_ms()
  # Return the unix time 15 mins from now
  return time_now_ms + unix_15

def mail_confirmation_code(mail_app, email_address, code):
  msg = Message('Secured Woof', sender = 'securedog@gmail.com', recipients = [str(email_address)])
  nl = '\n'
  msg.body = f"Confirmation code to authenticate into Secure Dog is:{nl}{code}{nl}{nl}Happy browsing!"
  msg.html = render_template('email/confirm_code.html', code=code)
  mail_app.send(msg)
  return True

def mail_analytics(mail_app, post_description):
  msg = Message('New post on secure-dog', sender = 'securedog@gmail.com', recipients = ["securedogapp@gmail.com"])
  msg.body = f"A new post was created {post_description} \n\nhttps://secure-dog.herokuapp.com/feed"
  mail_app.send(msg)
  return True

def check_email(email):   
  if(re.search(email_regex,email)):   
    return True
  else:
    return False

def validate_password(password):
  # Will raise an exception if not valid
  # The password should have at least:
  # six characters
  # one lowercase letter
  # one uppercase letter
  
  if len(password) < 6:
    raise ValueError

  if not any(char.islower() for char in password):
    raise ValueError

  if not any(char.isupper() for char in password):
    raise ValueError

def check_url(url):
  # Will raise an exception if not a valid URL
  value = validators.url(url)
  return value