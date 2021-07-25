import hashlib
from time import time
from Crypto.Signature import pkcs1_15

class Transaction:
	def __init__(self, fromAdress, toAdress, amount):
		self.fromAdress = fromAdress
		self.toAddress = toAdress

		self.amount = amount
		self.time = time()

		self.hash = self.transactionHash()


	def transactionHash(self):
		preHashData = '-'.join(self.sender + '-' + self.recipient + '-' + str(self.amount) + '-' + str(self.time))
		return hashlib.sha256(preHashData.encode()).hexdigest()


	def signTransaction(self, signKey):
		if signKey.public_key() != self.fromAdress:
			print('attempted signing from different wallet')
			return False

		txHash = self.transactionHash()

		if self.hash != txHash:
			print('sign error')
			return False
		
		self.signature = pkcs1_15.new(signKey).sign(txHash)

		return True


	def isValid(self):
		if self.fromAdress == self.toAddress:
			print('self send error')
			return False

		if self.hash != self.transactionHash():
			print('hashes do not match')
			return False

		if len(self.signature) <= 0 or not self.signature:
			print('transaction not signed')
			return False

		return True