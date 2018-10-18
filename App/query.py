import pyrebase

config = {
  "apiKey": "",
  "authDomain": "highonbot-fee46.firebaseapp.com",
  "databaseURL": "https://highonbot-fee46.firebaseio.com",
  "storageBucket": "highonbot-fee46.appspot.com"
}

emailId = "teamanything98@gmail.com"
password = "@random_bits" 

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

# Log the user in
user = auth.sign_in_with_email_and_password(emailId,password)

# Get a reference to the database service
db = firebase.database()

def refresh(user):
    user=auth.refresh(user['refreshToken'])

def addUser(senderId,SSH,userid,password,current_path):
  refresh(user)
  users=db.get(user['idToken']).val()
  users[senderId]=[SSH,userid,password,current_path]
  db.update(users)

def getUser(senderId):
  refresh(user)
  users=db.get(user['idToken']).val()
  if users.get(senderId,0):
    return users[senderId]
  else:
    return False

def getPath(senderId):
  refresh(user)
  users=db.get(user['idToken']).val()
  if users.get(senderId,0):
    return users[senderId][3]
  else:
    return False

def updatePath(senderId,path):
  refresh(user)
  users=db.get(user['idToken']).val()
  users[senderId][3]=path
  db.update(users)



if __name__ == "__main__":
  addUser("123","1912","1021","@dhw9hd")