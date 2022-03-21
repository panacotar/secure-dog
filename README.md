# Secure dog

The app will use 2FA to authenticate users

The users which got in, can see the juice of this webapp - a feed of dogs with sunglasses photos.


### 2FA
Will use the user's email address to send the OTP (one time password)

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
- token ([code + expiration date])

**posts table**
*posts owned_by user*
- id (PRIMARY)
- author (FOREIGN - user.id)
- photo_URL
- description
  

## ENV

Before starting this app, you need to create a config file under *instance/config.py* folder. 
The contents should be:

```
MAIL_USERNAME = 'email'
MAIL_PASSWORD = '***'
```

## Routes

#### 1. Register
This will display a form with 5 inputs:
- email (unique)
- username
- bio
- password
- confirm password
After submit:
1. validate the existance of email, username, password. 
2. hash the password 
3. create a Confirmation code + coded expiration date and add it to the list
4. create a new DB entry with this user
5. Move the user to the /confirmation screen and ask for the code

#### 2. Confirm
This will be used for both registering the users + login them in
We display a form with on input (confirmation code) + instruct the user to check their email.
After submit:
1. Validate the confirmation code
2. Check the submitted code with the one from the user
3. Check if the submitted code didn't expire yet
4. Remove the token after the first check
5. If fail, we move the user to /unconfirmed path.
6. If success, we change the *confirmed* field to true, save the user and we move the user to the homepage (feed)

#### 3. Login
This will have a normal form with email + password
After submit:
1. Validate the existence of the email + password
2. Check if the password is the same with the one from the DB
3. Display a flash message if password is not correct
4. Create a confirmation code + save it on the user [token, expiration_date] + mail the user
5. Move the user to the /confirm path and wait for the user to submit the code
6. Validate the token + the token expiration date
7. If success, we move the user to the homepage (feed)

#### 4. Homepage
We load the posts and display them to the user
We check for POST request and create new posts

## Error handling
The app handles the most common errors using the [errorhandler](https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.errorhandler) module from Flask.
The errors currently handled are:
- 404 - Not Found
- 403 - Forbidden
- 405 - Method Not Allowed
- 500 - Internal Server Error
For each of them, a different HTML template was created under the `templates/errors/` directory.