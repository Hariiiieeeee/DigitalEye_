from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import NLP_assessment

app = Flask(__name__, template_folder="templates")
app.secret_key = "3d0a015d132d43329c80c091edaa5dfa"

#mongodb config
client = MongoClient('mongodb://localhost:27017/')
db = client['InsureAI']
users_collection = db['users']
policy_details = db['policy_details']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

__username = None

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    global __username
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username' : username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            __username = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        else:
            flash('Invalid usename or password', 'danger')
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if users_collection.find_one({'username': username}):
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        users_collection.insert_one({
            'username': username,
            'email': email,
            'phone': phone,
            'password': hashed_password
        })

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/home', methods=['GET'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("home.html")

@app.route('/details')
def details():
    return render_template('details.html')

@app.route('/submit_claim_details', methods=['POST'])
def submit_claim_details():
    
        # fullname = request.form['full-name']
        # contact = request.form['contact-number']
        # email = request.form['email']
        # address = request.form['address']

        # vehiclenumber = request.form['vehicle-number']
        # drivername = request.form['driver-name']
        # licensenumber = request.form['license-number']
        # alcohol = request.form['alcohol-drugs']

        # policynumber = request.form['policy-number']
        # insurername = request.form['insurer-name']

        # incidentdate = request.form['incident-date']
        # incidenttime = request.form['incident-time']
        # incidentlocation = request.form['incident-location']

        # policereport = request.form['police-report']
        # policestation = request.form['police-station']
        # accidentcausedby = request.form['accident-caused-by']

        # otherinjuries = request.form['other-injured']
        # injuredname = request.form['injured-name']
        # thirdpartyvehiclenumber = request.form['injured-vehicle-number']

        accidentdescription = request.form['description-of-accident']
        image_name = request.form['damage-image']

        response = jsonify({
        "locations": NLP_assessment.match_labels_nlp(accidentdescription, image_name)
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
    
        return response
    
@app.route('/policy_status')
def policy_status():
    return render_template('policy_status.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)