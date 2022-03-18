from random import randint
import time
from flask import redirect, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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

