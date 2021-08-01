from app.src.genkey import genKey
from app import db


class User(db.Model):
	name = db.Column(db.String(30), nullable=False)
	username = db.Column(db.String(30), primary_key=True)
	password = db.Column(db.String(40), nullable=False)
	email = db.Column(db.String(50), primary_key=True) # email as primary key
	balance = db.Column(db.Integer, nullable=False)
	publicKey = db.Column(db.String(500), nullable=False)

	def __init__(self, name, username, password, email):
		self.name = name
		self.username = username
		self.password = password
		self.email = email
		self.publicKey = genKey(self.username)
		self.balance = 50

	def __repr__(self):
		return f'User {self.username} {self.name} {self.email}'

	def dictify(self):
		return {'name': self.name, 'username': self.username, 'email': self.email, 'balance': self.balance, 'publicKey': self.publicKey}

# # TRANSACTION CLASS
# class Transaction(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	sender = db.Column(db.String(30), nullable=False)
# 	recipient = db.Column(db.String(30), nullable=False)
# 	senderKey = db.Column(db.String(500), nullable=False)
# 	recipientKey = db.Column(db.String(500), nullable=False)
# 	amount = db.Column(db.Integer, nullable=False)
# 	time = db.Column(db.String(50), nullable=False)
# 	userId = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)

# 	def __init__(self, sender, recipient, amount, userId):
# 		self.sender = sender.username
# 		self.recipient = recipient.username
# 		self.senderKey = sender.publicKey
# 		self.recipientKey = recipient.publicKey
# 		self.amount = amount
# 		self.time = getLocalTime()
# 		self.userId = userId.username

# 	def __repr__(self):
# 		return f'Transaction from {self.sender} to {self.recipient} of amount {self.amount} at {self.time}'

# 	def dictify(self):
# 		return {'id': self.id, 'sender': self.sender, 'recipient': self.recipient, 'amount': self.amount, 'time': self.time} 