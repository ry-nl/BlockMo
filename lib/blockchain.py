import hashlib
from time import time

class BlockChain:
	def __init__(self):
		self.chain = []

	def encodeJSON(self):
		chainJSON = []

		for block in self.chain:
			blockJSON = {}
			blockJSON['block hash'] = block.hash
			blockJSON['prev hash'] = block.prevHash

			chainJSON.append(blockJSON)

		return chainJSON

	def getPrevBlock(self):
		return self.chain[-1]

	def addBlock(self, block):
		if len(self.chain) > 0:
			block.prevHash = self.getPrevBlock().hash
		else: 
			block.prevHash = 'none';
			
		self.chain.append(block)

class Block:
	def __init__(self, transactions, time, id):
		self.time = time
		self.id = id

		self.transactions = transactions
		self.prevHash = ''

		self.hash = self.blockHash()

	def blockHash(self):
		strTransactions = ''
		for transaction in self.transactions:
			strTransactions += transaction

		preHashData = '-'.join(str(self.id) + '-' + strTransactions  + '-' + self.prevHash + '-' + str(self.time))
		return hashlib.sha256(preHashData.encode()).hexdigest()	

class Transaction:
	def __init__(self, sender, receiver, amount):
		self.sender = sender
		self.receiver = receiver

		self.amount = amount
		self.time = time()

		self.hash = self.transactionHash()

	def transactionHash(self):
		preHashData = '-'.join(self.sender + '-' + self.receiver + '-' + str(self.amount) + '-' + str(self.time))
		return hashlib.sha256(preHashData.encode()).hexdigest()
