from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)

# database creation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = '6ALc723hiM9mEJAr5t6'
app.permanent_session_lifetime = timedelta(minutes=20)
db = SQLAlchemy(app)

# user class
class User(db.Model):
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), primary_key=True) # email as primary key
    balance = db.Column(db.Integer, nullable=False)

    def __init__(self, name, username, password, email):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.balance = 0

    def __repr__(self):
        return f'User {self.username} {self.name} {self.email}'


@app.route('/')
def home():
    user = None
    if 'user' in session:
        user = session['user']
    return render_template('index.html', user=user)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    pass


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/createaccount/', methods=['GET', 'POST'])
def createAccount():
    user = None
    # if form is submitted
    if request.method == 'POST':
        # get username and email from sign up form
        username = request.form['username']
        email = request.form['email']
        # find username and email from database
        userByUsername = User.query.filter_by(username=username).first()
        userByEmail = User.query.filter_by(email=email).first()
        # if exist in database, flash message and redirect to page
        if userByUsername or userByEmail:
            # since email is primary key, if email already exists, ask to log in
            if userByEmail:
                flash('Email already registered, please log in')
            # if username already exists, ask to choose another
            else:
                flash('Username taken, please choose another')
            # redirect to create account page
            return render_template('createaccount.html', user=user)
        # if new user, get remaining user info
        name = request.form['name']
        password = request.form['password']
        # create user
        user = User(name, username, password, email)
        # add user to session
        session['user'] = user.name
        # add user to database
        db.session.add(user)
        db.session.commit()
        # redirect to home if logged in
        return redirect(url_for('home'))
    # if page is pulled up via navbar
    else:
        # render create account page
        return render_template('createaccount.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
