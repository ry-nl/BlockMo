from time import time
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

class Transaction:
	def __init__(self, fromAddress, toAddress, amount):
		self.fromAddress = fromAddress
		self.toAddress = toAddress

		self.amount = amount
		self.time = time()

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

		print(signKey.export_key())
		
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