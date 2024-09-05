from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import firebase_admin 
from firebase_admin import credentials, auth

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'C:\Users\loges\java\.dist\skin_diseases\skindiseasedetection-a482a-firebase-adminsdk-p75lp-35ab1dd7ee.json')
firebase_admin.initialize_app(cred)

# MongoDB configuration
mongo_uri = 'mongodb://localhost:27017/InsureAI'
client = MongoClient(mongo_uri)
db_mongo = client.get_database('skin_disease_detector')
users_collection = db_mongo.users
app.route('/')
def home():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            username = user.get('username', 'Guest')  # Default to 'Guest' if username not found
            return render_template('index.html', username=username)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check user in MongoDB
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        if users_collection.find_one({'email': email}):
            flash('Email already registered')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'email': email, 'password': hashed_password, 'username': request.form['username']})

        # Create a user in Firebase Authentication
        try:
            auth.create_user(email=email, password=password)
        except Exception as e:
            logger.error(f"Error creating Firebase user: {e}")
            flash('User registration failed')
            return redirect(url_for('register'))

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)