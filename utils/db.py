from dotenv import load_dotenv
load_dotenv() 

import psycopg2
import psycopg2.extras
import os


def to_dict(dict_cursor: tuple):
  arr = []
  for tup in dict_cursor:
    arr.append(dict(tup))
  return arr


def connect_db():
  try:
    return psycopg2.connect(os.getenv("DATABASE_CONNECT_PARAMS"))
  except:
    print("Error connecting to DB")


def get_user_by_email(email):
  if not email: 
    print("No email provided")
    return False
  con = connect_db()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    # cur.execute("SELECT * FROM users;")
  except:
    print("Error getting user by email")
  
  res = cur.fetchall()

  print("RESPONSE DB select")
  print(res)

  # con.commit()
  cur.close()
  con.close()
  return res
  

def register_user(email, hash, username, token):
  con = connect_db()
  cur = con.cursor()

  try:
    # cur.execute("INSERT INTO users (email, username, hash, token) VALUES (%s, %s, %s, %s)", (email,username,hash,token,))
    cur.execute(
      "INSERT INTO \
        users (email, username, hash, token) \
      VALUES (%s, %s, %s, %s)", (
        email,
        username,
        hash,
        token,
      )
    )
  except psycopg2.ProgrammingError as err:
    print("Error registering user")
    print(err)
  
  # res = cur.fetchone()

  print("RESPONSE DB INSERT")
  # print(res)

  con.commit()
  cur.close()
  con.close()
  return True


def update_user(id, column, value):
  con = connect_db()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
    cur.execute(
      "UPDATE users SET %s=%s WHERE id = %s", 
      (
        column,
        value,
        id,
      )
    )
  except:
    print("Error updating user")

  con.commit()
  cur.close()
  con.close()
  return True


def get_posts():
  con = connect_db()
  cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

  try:
    cur.execute("SELECT * FROM posts ORDER BY created_at DESC")
  except:
    print("Error updating user")

  try:
    result = cur.fetchall()
    res = to_dict(result)
  except:
    print("No posts yet")
    return []

  cur.close()
  con.close()
  return res