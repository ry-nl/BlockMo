from flask import render_template, redirect, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from .models import app, User, Transaction
# import lib.blockchain as blockchain

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
            if bcrypt.check_password(password.encode('utf-8'), user.password):
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

# TEST FUNCTION TO VIEW DATABASE
@app.route('/viewDB/')
def viewDB():
    user = getUserFromSession()
    return render_template('viewDB.html', user=user, currentPage='viewDB', values=User.query.all())

# HELPER FUNCTION TO GET USER FROM SESSION
def getUserFromSession():
    if 'user' in session:
        return session['user']
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
