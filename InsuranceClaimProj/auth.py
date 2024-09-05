from flask import Flask, render_template, url_for, redirect, request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import firebase_admin
from firebase_admin import credentials, auth, firestore

app = Flask(__name__)
app.secret_key = "3d0a015d132d43329c80c091edaa5dfa"

#firebase init
cred = credentials.Certificate("server\insureai2024-firebase-adminsdk-c8cjo-b29d745597.json")
firebase_admin.initialize_app(cred)

# Firestore database
db = firestore.client()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Loader
@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return User(user_data['username'], user_data['password'], user_id)
    return None

# User class
class User(UserMixin):
    def __init__(self, username, password, user_id=None):
        self.id = user_id
        self.username = username
        self.password = password

# Registration Form
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user = db.collection('users').where('username', '==', username.data).get()
        if existing_user:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

# Login Form
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template("#")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_query = db.collection('users').where('username', '==', form.username.data).get()
        if user_query:
            user_data = user_query[0].to_dict()
            if auth.verify_password_hash(user_data['password'], form.password.data):
                user = User(user_data['username'], user_data['password'], user_query[0].id)
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

#render dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

#render logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = auth.generate_password_hash(form.password.data)
        new_user = {
            'username': form.username.data,
            'password': hashed_password
        }
        db.collection('users').add(new_user)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
