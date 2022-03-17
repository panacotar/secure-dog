# Secure dog
#### Video Demo:  <URL HERE>
#### Description:
TODO
The app will use 2FA to authenticate users

The users which got in, can see the juice of this webapp - a feed of dogs with sunglasses photos.

### 2FA
Will use the user's email address to send the OTP (one time password)

### DB Schema
**users table**
*users has_many posts*
- id (PRIMARY)
- email
- username
- profile_photo_url
- bio

**posts table**
*posts owned_by user*
- id (PRIMARY)
- author (FOREIGN - user.id)
- photo_URL
- description

### ENV
Before starting this app, you need to create a config file under *instance/config.py* folder. The contents should be:
```
MAIL_USERNAME = 'email'
MAIL_PASSWORD = '***'

```