from time import localtime
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

class Transaction:
	def __init__(self, sender, fromAddress, recipient, toAddress, amount):
		self.fromAddress = fromAddress
		self.toAddress = toAddress

		self.sender = sender
		self.recipient = recipient

		self.amount = amount
		self.time = self.getTransactionTime()

		self.hash = self.transactionHash().hexdigest()
		self.SHAhash = self.transactionHash()


	def transactionHash(self):
		preHashData = '-'.join(str(self.fromAddress) + '-' + str(self.toAddress) + '-' + str(self.amount) + '-' + str(self.time))
		return SHA256.new(preHashData.encode('utf-8'))


	def signTransaction(self, signKey):
		if signKey.public_key().export_key('PEM') != self.fromAddress:
			print('attempted signing from different wallet')
			return False

		if self.hash != self.transactionHash().hexdigest():
			print('sign error')
			return False

		self.signature = pkcs1_15.new(signKey).sign(self.SHAhash)

		return True


	def isValid(self):
		if self.fromAddress == 'System' and self.toAddress:
			return True

		if self.fromAddress == self.toAddress:
			print('self send error')
			return False

		if self.fromAddress == None:
			return True

		if self.hash != self.transactionHash().hexdigest():
			print('hashes do not match')
			return False

		if len(self.signature) <= 0 or not self.signature:
			print('transaction not signed')
			return False
		
		senderKey = RSA.importKey(self.fromAddress)

		try: 
			pkcs1_15.new(senderKey).verify(self.SHAhash, self.signature)
		except:
			print('failed to verify signature')
			return False	

		return True


	def getTransactionTime(self):
		timeStruct = localtime()
		timeString = ':'.join([str(timeStruct[3]), str(timeStruct[4]).zfill(2)])
		dateString = '/'.join([str(timeStruct[1]), str(timeStruct[2]), str(timeStruct[0])[2:]])
		return timeString + ' - ' + dateString

	
	def dictify(self):
		return {'fromAddress': self.fromAddress, 'toAddress': self.toAddress, 'sender': self.sender, 'recipient': self.recipient, 'amount': self.amount, 'time': self.time}