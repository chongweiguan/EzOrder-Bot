import pyrebase

firebaseConfig = {
  "apiKey": "AIzaSyCyA1ZkuzJsxOR0-CdXhoMfTr4tT6_bCWM",
  "authDomain": "ezorderbot-32361.firebaseapp.com",
  "databaseURL": "https://ezorderbot-32361-default-rtdb.asia-southeast1.firebasedatabase.app/",
  "projectId": "ezorderbot-32361",
  "storageBucket": "ezorderbot-32361.appspot.com",
  "messagingSenderId": "1001383637914",
  "appId": "1:1001383637914:web:211e440b4a0c3f2046c023"
}


firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
