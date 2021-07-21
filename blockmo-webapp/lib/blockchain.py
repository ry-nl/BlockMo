import hashlib
from time import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

class BlockChain:
	def __init__(self):
		self.index = 1
		self.chain = [self.genesisBlock()]
		self.difficulty = 2
		self.unfulfilledTransactions = []


	def genesisBlock(self):
		return Block(0, [], time())


	def generateKeys(self):
			key = RSA.generate(2048)
			private_key = key.export_key()
			file_out = open("private.pem", "wb")
			file_out.write(private_key)
			file_out.close()

			public_key = key.publickey().export_key()
			file_out = open("public.pem", "wb")
			file_out.write(public_key)
			file_out.close()

			return public_key.decode('ASCII')


	def makeTransaction(self, sender, recipient, amount, senderKey1, senderKey2):
		if not sender or not recipient or not amount:
			return False

		senderKey1_encoded = senderKey1.encode('ASCII')
		senderKey2_encoded = senderKey2.encode('ASCII')

		key1 = RSA.importKey(senderKey1_encoded)
		key2 = RSA.importKey(senderKey2_encoded)

		transaction = Transaction(sender, recipient, amount)
		transaction.signTransaction(key1, key2)

		if not transaction.isValid():
			print('Invalid Transaction')
			return False

		print('Valid Transaction!')

		self.unfulfilledTransactions.append(transaction)
		return True


	def encodeJSON(self):
		chainJSON = []

		for block in self.chain:
			blockJSON = {}
			blockJSON['block hash'] = block.hash
			blockJSON['prev hash'] = block.prevHash
			blockJSON['transactions'] = block.transactions

			chainJSON.append(blockJSON)

		return chainJSON


	def getPrevBlock(self):
		return self.chain[-1]


	def addBlock(self, block):
		block.prevHash = self.getPrevBlock().hash
		block.mineBlock(self.difficulty)
		self.chain.append(block)


	def mineTransactions(self):
		if len(self.unfulfilledTransactions) <= 1:
			print('Insufficient Outstanding Transactions')
			return False

		for slice in range(0, len(self.unfulfilledTransactions), 10):
			sliceEnd = slice + 10
			if sliceEnd >= len(self.unfulfilledTransactions):
				sliceEnd = len(self.unfulfilledTransactions)

			blockTransactions = self.unfulfilledTransactions[slice: sliceEnd]

			block = Block(len(self.chain), blockTransactions, time())
			self.addBlock(block)

		self.unfulfilledTransactions.clear()


class Block:
	def __init__(self, id, transactions, time):
		self.time = time
		self.id = id

		self.transactions = transactions
		self.prevHash = 'none'
		self.nonce = 0
		self.hash = self.blockHash()


	def blockHash(self):
		strTransactions = ''
		for transaction in self.transactions:
			strTransactions += transaction.hash

		preHashData = '-'.join(str(self.id) + '-' + strTransactions  + '-' + self.prevHash + '-' + str(self.time) + '-' + str(self.nonce))
		return hashlib.sha256(preHashData.encode()).hexdigest()	


	def mineBlock(self, difficulty):
		solveRequirement = ''.join(['0'] * difficulty)
		while self.hash[0:difficulty] != solveRequirement:
			self.nonce += 1
			self.hash = self.blockHash()


class Transaction:
	def __init__(self, sender, recipient, amount):
		self.sender = sender
		self.recipient = recipient

		self.amount = amount
		self.time = time()

		self.hash = self.transactionHash()


	def transactionHash(self):
		preHashData = '-'.join(self.sender + '-' + self.recipient + '-' + str(self.amount) + '-' + str(self.time))
		return hashlib.sha256(preHashData.encode()).hexdigest()


	def signTransaction(self, key, senderKey):
		if self.hash != self.transactionHash():
			print('Sign error 1')
			return False

		if str(key.publickey().export_key()) != str(senderKey.publickey().export_key()):
			print('Sign error 2')
			return False

		pkcs1_15.new(key)

		self.signature = 'signed'
		return True


	def isValid(self):
		if self.sender == self.recipient:
			return False

		if self.hash != self.transactionHash():
			return False

		if len(self.signature) <= 0 or not self.signature:
			return False

		return True