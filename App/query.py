import pyrebase
from config import * 

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password(emailId,password)

# Get a reference to the database service
db = firebase.database()

def refresh(user):
    user=auth.refresh(user['refreshToken'])

def addUser(senderId,SSH,userid,password):
  refresh(user)
  users=db.get(user['idToken']).val()
  users[senderId]=[SSH,userid,password]
  db.update(users)

def getUser(senderId):
  refresh(user)
  users=db.get(user['idToken']).val()
  return users[senderId]