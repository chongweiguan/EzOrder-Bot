import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyAMIjHkOJsMOI1deAKaMxWHy2NEWQUYwdM",
    "authDomain": "ezordertesting-2f378.firebaseapp.com",
    "databaseURL": "https://ezordertesting-2f378-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "ezordertesting-2f378",
    "storageBucket": "ezordertesting-2f378.appspot.com",
    "messagingSenderId": "329470688965",
    "appId": "1:329470688965:web:6b62dadd02f3edc0eefaac",
    "measurementId": "G-9Y8X2BHNCR"
}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
