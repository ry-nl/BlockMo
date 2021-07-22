from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from time import time, localtime
import lib.blockchain as blockchain


app = Flask(__name__)

# database creation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '6ALc723hiM9mEJAr5t6'
app.permanent_session_lifetime = timedelta(minutes=20)
db = SQLAlchemy(app)

# user class
class User(db.Model):
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), primary_key=True) # email as primary key
    balance = db.Column(db.Integer, nullable=False)
    transactions = db.relationship('Transaction', backref='party', lazy=True)

    def __init__(self, name, username, password, email):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.balance = 50

    def __repr__(self):
        return f'User {self.username} {self.name} {self.email}'

    def dictify(self):
        return {'name': self.name, 'username': self.username, 'email': self.email, 'balance': self.balance}


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


@app.route('/')
def home():
    user = None
    if 'user' in session:
        user = session['user']
    return render_template('index.html', user=user, currentPage='home')


@app.route('/send/', methods=['GET', 'POST'])
def send():

    user = getUserFromSession()

    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipientUsername = request.form['recipient']
        transactionAmount = request.form['amount']

        recipient = User.query.filter_by(username=recipientUsername).first()
        sender = User.query.filter_by(username=user['username']).first()

        if sender == recipient:
            flash('Self send request invalid')
            return render_template('send.html', user=user, currentPage='send')

        if not recipient:
            flash('Recipient does not exist')
            return render_template('send.html', user=user, currentPage='send')

        if sender.balance < int(transactionAmount):
            flash('Transaction amount exceeds funds available')
            return render_template('send.html', user=user, currentPage='send')

        if int(transactionAmount) <= 0:
            flash('Enter valid amount to be sent')
            return render_template('send.html', user=user, currentPage='send')

        sender.balance -= int(transactionAmount)
        recipient.balance += int(transactionAmount)

        senderTransaction = Transaction(sender.username, recipient.username, int(transactionAmount), sender.username)
        recipientTransaction = Transaction(sender.username, recipient.username, int(transactionAmount), recipient.username)
        
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

        flash(f'Amount of {transactionAmount} has been successfully sent to {recipient.username}')
        return render_template('send.html', user=user, currentPage='send')
    else:
        return render_template('send.html', user=user, currentPage='send')


@app.route('/transactions/')
def transactions():
    
    userData = getUserFromSession()

    if not userData:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=userData['username']).first()
    userTransactionsList = user.transactions
    userTransactions = []
    for transaction in userTransactionsList:
        userTransactions.insert(0, transaction.dictify())

    return render_template('transactions.html', user=userData, transactions=userTransactions, currentPage='transactions')
    

@app.route('/login/', methods=['GET', 'POST'])
def login():

    if getUserFromSession():
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user: 
            if user.password == password:
                session['user'] = user.dictify()
                return redirect(url_for('home'))
            else:
                flash('Password is incorrect')
                return render_template('login.html', currentPage='login')

        flash('Username is incorrect or is not registered')
        return render_template('login.html', currentPage='login')
    else:
        return render_template('login.html', currentPage='login')


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
            return render_template('createaccount.html', user=user, currentPage='createaccount')
        # if new user, get remaining user info
        name = request.form['name']
        password = request.form['password']
        # create user
        user = User(name, username, password, email)
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
    # if page is pulled up via navbar
    else:
        # render create account page
        return render_template('createaccount.html', user=user, currentPage='createaccount')


@app.route('/viewDB/')
def viewDB():
    user = getUserFromSession()
    return render_template('viewDB.html', user=user, currentPage='viewDB', values=User.query.all())


def getUserFromSession():
    if 'user' in session:
        return session['user']
    else:
        return None


def getLocalTime():
    timeStruct = localtime()
    timeString = ':'.join([str(timeStruct[3]), str(timeStruct[4]).zfill(2)])
    dateString = '/'.join([str(timeStruct[1]), str(timeStruct[2]), str(timeStruct[0])[2:]])
    return timeString + ' - ' + dateString


if __name__ == '__main__':
    app.run(debug=True)
