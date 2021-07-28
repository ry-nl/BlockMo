from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import smtplib
import secrets
from datetime import timedelta
from time import localtime
from src.chain import *
from src.genkey import genKey

# ---------- APP CONFIG ----------

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '6ALc723hiM9mEJAr5t6'
app.permanent_session_lifetime = timedelta(minutes=20)
db = SQLAlchemy(app)

# ---------- MODELS ----------

# USER CLASS
class User(db.Model):
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(50), primary_key=True) # email as primary key
    balance = db.Column(db.Integer, nullable=False)
    # publicKey = db.Column(db.String(500), nullable=False)
    transactions = db.relationship('Transaction', backref='party', lazy=True)

    def __init__(self, name, username, password, email):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        # self.publicKey = genKey()
        self.balance = 50

    def __repr__(self):
        return f'User {self.username} {self.name} {self.email}'

    def dictify(self):
        return {'name': self.name, 'username': self.username, 'email': self.email, 'balance': self.balance}

# TRANSACTION CLASS
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(20), nullable=False)
    recipient = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    userId = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)

    def __init__(self, sender, recipient, amount, userId):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.time = getLocalTime()
        self.userId = userId
    
    def __repr__(self):
        return f'Transaction from {self.sender} to {self.recipient} of amount {self.amount} at {self.time}'

    def dictify(self):
        return {'id': self.id, 'sender': self.sender, 'recipient': self.recipient, 'amount': self.amount, 'time': self.time}

# ---------- ROUTES ----------

# HOME ROUTE
@app.route('/')
def home():
    user = None
    if 'user' in session:
        user = session['user']
    return render_template('index.html', user=user, currentPage='home')

# SEND ROUTE
@app.route('/send/', methods=['GET', 'POST'])
def send():
    # get user in session
    user = getUserFromSession()
    # if user is not logged in, send to login page
    if not user:
        return redirect(url_for('login'))
    # if form is submitted
    if request.method == 'POST':
        # get the recipient username and transaction amount from the form
        recipientUsername = request.form['recipient']
        transactionAmount = request.form['amount']
        # get the recipient and the sender from the database
        recipient = User.query.filter_by(username=recipientUsername).first()
        sender = User.query.filter_by(username=user['username']).first()
        # make sure user is not self sending
        if sender == recipient:
            flash('Self send request invalid')
            return render_template('send.html', user=user, currentPage='send')
        # make sure there is a recipient
        if not recipient:
            flash('Recipient does not exist')
            return render_template('send.html', user=user, currentPage='send')
        # make sure the user balance is sufficient
        if sender.balance < int(transactionAmount):
            flash('Transaction amount exceeds funds available')
            return render_template('send.html', user=user, currentPage='send')
        # make sure transaction amount is non-zero and non-negative
        if int(transactionAmount) <= 0:
            flash('Enter valid amount to be sent')
            return render_template('send.html', user=user, currentPage='send')
        # TEMPORARY
        # edit balances
        sender.balance -= int(transactionAmount)
        recipient.balance += int(transactionAmount)
        # create transaction objects
        senderTransaction = Transaction(sender.username, recipient.username, int(transactionAmount), sender.username)
        recipientTransaction = Transaction(sender.username, recipient.username, int(transactionAmount), recipient.username)
        # add transactions to the database 
        try:
            db.session.add(senderTransaction)
            db.session.add(recipientTransaction)
            db.session.commit()
        except:
            db.rollback()
            sender.balance += int(transactionAmount)
            recipient.balance -= int(transactionAmount)
            flash('Error adding transaction to database')
            return render_template('send.html', user=user, currentPage='send')
        # show success message and render send page
        flash(f'Amount of {transactionAmount} has been successfully sent to {recipient.username}')
        return render_template('send.html', user=user, currentPage='send')
    # if page is pulled up
    else:
        return render_template('send.html', user=user, currentPage='send')

# TRANSACTIONS ROUTE
@app.route('/transactions/')
def transactions():
    # get user in session
    userData = getUserFromSession()
    # if user is not logged in, send to login page
    if not userData:
        return redirect(url_for('login'))
    # get user from database
    user = User.query.filter_by(username=userData['username']).first()
    # get user's transactions
    userTransactionsList = user.transactions
    userTransactions = []
    for transaction in userTransactionsList:
        userTransactions.insert(0, transaction.dictify())
    # render transaction page and display user transaction history
    return render_template('transactions.html', user=userData, transactions=userTransactions, currentPage='transactions')
    
# LOG IN ROUTE
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # if a user is already logged in, redirect to home page
    if getUserFromSession():
        return redirect(url_for('home'))
    # if form is submitted
    if request.method == 'POST':
        # get username and password
        username = request.form['username']
        password = request.form['password']
        # attempt to find user with same username
        user = User.query.filter_by(username=username).first()
        # if the user exists
        if user: 
            # check if password matches hashed password
            if bcrypt.checkpw(password.encode('utf-8'), user.password):
                # add user to session
                session['user'] = user.dictify()
                return redirect(url_for('home'))
            else:
                flash('Password is incorrect')
                return render_template('login.html', currentPage='login')
        # if user does not exist
        flash('Username is incorrect or is not registered')
        return render_template('login.html', currentPage='login')
    # if page is pulled up
    else:
        return render_template('login.html', currentPage='login')

# LOG OUT ROUTE
@app.route('/logout/')
def logout():
    # remove user from sesson
    session.pop('user', None)
    return redirect(url_for('home'))

# CREATE ACCOUNT ROUTE
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
            return render_template('createaccount.html', user=user, currentPage='createaccount')
        # if new user, get remaining user info
        name = request.form['name']
        password = request.form['password']
        # hash the password to be stored
        hashedPassword = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        # create user
        user = User(name, username, hashedPassword, email)
        # add user to session
        session['user'] = user.dictify()
        # add user to database
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding user to database')
            return render_template('createaccount.html', user=user, currentPage='createaccount')
        # redirect to home if logged in
        return redirect(url_for('home'))
    # if page is pulled up
    else:
        # render create account page
        return render_template('createaccount.html', user=user, currentPage='createaccount')

# @app.route('/createaccount/', methods=['GET', 'POST'])
# def createAccount():
#     # if a user is already logged in redirect to home
#     if getUserFromSession():
#         return redirect(url_for('home'))
#     # if form is submitted
#     if request.method == 'POST':
#         # get username and email from sign up form
#         username = request.form['username']
#         email = request.form['email']
#         # find username and email from database
#         userByUsername = User.query.filter_by(username=username).first()
#         userByEmail = User.query.filter_by(email=email).first()
#         # if exist in database, flash message and redirect to page
#         if userByUsername or userByEmail:
#             # since email is primary key, if email already exists, ask to log in
#             if userByEmail:
#                 flash('Email already registered, please log in')
#             # if username already exists, ask to choose another
#             else:
#                 flash('Username taken, please choose another')
#             # redirect to create account page
#             return render_template('createaccount.html', user=user, currentPage='createaccount')
#         # if new user, get remaining user info
#         name = request.form['name']
#         password = request.form['password']
#         # hash the password to be stored
#         hashedPassword = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
#         # create user
#         user = User(name, username, hashedPassword, email)
#         session['unverifiedUser'] = user.dictify()
#         session['unverifiedUserPW'] = hashedPassword
#         return redirect(url_for('emailAuthorize'))
#     # if page is pulled up
#     else:
#         # user's email has been verified
#         if session.get('isVerified', None):
#             # add user to session
#             session['user'] = session['unverifiedUser']
#             # create user object to be stored in database
#             user = User(session['user']['name'], session['user']['username'], session['unverifiedUserPW'], session['user']['email'])
#             # remove all sensitive and temporary data from the session
#             session.pop('isVerified', None)
#             session.pop('unverifiedUser', None)
#             session.pop('unverifiedUserPW', None)
#             # add user to database
#             try:
#                 db.session.add(user)
#                 db.session.commit()
#             except:
#                 db.session.rollback()
#                 flash('Error adding user to database')
#                 return render_template('createaccount.html', currentPage='createaccount')
#             # redirect to home if logged in
#             return redirect(url_for('home'))
#         # user's email has not yet been verified
#         else:
#             return render_template('createaccount.html', currentPage='createaccount')

# # AUTHORIZE EMAIL ROUTE
# @app.route('/emailauthorize/', methods = ['POST', 'GET'])
# def emailAuthorize():
    
#     if not session.get('unverifiedUser', None):
#         return redirect(url_for('home'))

#     if request.method == 'POST':
        
#         userToken = request.form['Email Authorization Key']
#         if userToken == session['userAuthorKey']:
#             session.pop('userAuthorKey', None)

#             session['isVerified'] = True
#             return redirect(url_for('createAccount'))
#         else:
#             return render_template('emailauthorize.html', currentPage='emailauthorize')
#     else:
#         #email log in to send to user
#         sender = "testDummy2113@gmail.com"
#         receiver =  session['unverifiedUser']['email']
#         password = "throwuponmybal"
#         subject = "BLOCKMO AUTHORIZATION KEY"
#         authenticationEmail = secrets.token_hex(3)
#         session['userAuthorKey'] = authenticationEmail
#         body = "Case sensitive authorization key: " + authenticationEmail
#         #header
#         message = f"""From: {sender}
#         To: {receiver}
#         Subject: {subject}\n
#         {body}
#         """
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         try:
#             server.login(sender, password)
#             server.sendmail(sender, receiver, message)
#         except smtplib.SMTPAuthenticationError:
#             pass
#         return render_template('emailauthorize.html', currentPage='emailauthorize')

# VIEW ACCOUNT ROUTE
@app.route('/viewaccount/')
def viewaccount():
    user = getUserFromSession()

    if not user:
        return redirect(url_for('login'))

    return render_template('viewaccount.html', user=user, currentPage='viewaccount')

# TEMPORARY ROUTE TO VIEW DATABASE
@app.route('/viewDB/')
def viewDB():
    user = getUserFromSession()
    return render_template('viewDB.html', user=user, currentPage='viewDB', values=User.query.all())

# ---------- HELPERS ----------

# GET USER FROM SESSION HELPER 
def getUserFromSession():
    if 'user' in session:
        return session['user']
    else:
        return None

# GET LOCAL TIME HELPER
def getLocalTime():
    timeStruct = localtime()
    timeString = ':'.join([str(timeStruct[3]), str(timeStruct[4]).zfill(2)])
    dateString = '/'.join([str(timeStruct[1]), str(timeStruct[2]), str(timeStruct[0])[2:]])
    return timeString + ' - ' + dateString

# ---------- APP INIT ----------

if __name__ == '__main__':
    app.run(debug=True)
