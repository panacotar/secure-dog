

# Secure dog

The app will use 2FA to authenticate users

The users which got in, can see the juice of this webapp - a feed of dogs with sunglasses photos.

### 2FA

Initially, Secure Dog will use a confirmation code sent by email as the second auth layer. This confirmation code consists of numbers and has a length of 6, ex:
```
123456
```

### Technologies
Written in Python3 and built with Flask web framework, HTML templating was done using the Jinja template engine.

As a first version, it utilizes SQLite3 as the Database. The app is currently hosted on Heroku.

## DB Schema

**users table**

*users has_many posts*

- id (PRIMARY)
- email
- username
- hash
- profile_photo_url
- bio
- confirmed
- token (list with [code + expiration date] )
 

**posts table**

*posts owned_by user*
- id (PRIMARY)
- author_id (FOREIGN - user.id)
- author_username
- photo_URL
- description

## ENV

Before starting this app, you need to create an `.env` file under the root directory.

The contents should be the config from your mail client:

```
MAIL_USERNAME="email"
MAIL_PASSWORD="***"
```

## Routes

#### 1. Homepage

#### 2. Register
This will display a form with 5 inputs:
- email (unique)
- username
- password
- confirm password

After submit:

1. validate the existence of *email*, *username*, *password*.
2. hash the password
3. create a Confirmation code + get expiration date (15 mins) and add it to the list
4. create a new DB entry with this user
5. Move the user to the */confirmation* screen and ask for the code

#### 3. Login
This will have a minimal form with only email + password

After submit:

1. Validate the existence of the email + password
2. Check if the password is the same with the one from the DB
3. Display a flash message if password is not correct
4. Create a confirmation code + save it on the user [token, expiration_date] + mail the user
5. Move the user to the /confirm path and wait for the user to submit the code
6. Validate the token + the token expiration date
7. If success, we move the user to the homepage (feed)

#### 4. Confirm
This will be used for both registering + login the users.

We display a form with on input (confirmation code) + instruct the user to check their email.

After submit:

1. Validate the confirmation code
2. Compare the submitted code with the one in the DB
3. Check if the submitted code didn't expire already
4. Remove the token after the first check
5. If fail, we move the user back to /login path.
6. If success, we change the *confirmed* field to true, save the user and we move the user to the homepage (/feed)

#### 5. Feed
We load the posts and display them to the user
We check for POST request and create new posts

#### Error routes
Currently we're catching HTTP errors and display different fallback page. Check the **Error Handling** section on the README for more details on this.

## Error handling
The app handles the most common errors using the [errorhandler](https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.errorhandler) module from Flask.

The errors currently handled are:
- 404 - Not Found
- 403 - Forbidden
- 405 - Method Not Allowed
- 500 - Internal Server Error

For each of them, a different HTML template was created under the `templates/errors/` directory.

## Misc
### Some things learned from this project
- Create and handle a Two Factor Auth flow
- Raise and handle exceptions in Python
- Handle erros in Flask
- Create a db + tables
- Use the 'include' statement from Jinja
- Send email in a Flask app using the flask_mail library
- Register and load environment variables using dotenv module
- Validate an URL using the *validators* module from validator_collection lib
- Load static files in a Flask app

### Future features time
- Upload image and save them to the DB
- Allow users to upload an avatar photo
- Forget password path
- Send the confirmation code by SMS. Allow users to choose between email and SMS