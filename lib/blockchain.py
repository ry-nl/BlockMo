import hashlib
from time import time

class BlockChain:
	def __init__(self):
		self.chain = [self.genesisBlock()]
		self.difficulty = 5


	def genesisBlock(self):
		return Block(0, [], time())


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
		block.prevHash = self.getPrevBlock().hash
		block.mineBlock(self.difficulty)
		self.chain.append(block)


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
			strTransactions += transaction

		preHashData = '-'.join(str(self.id) + '-' + strTransactions  + '-' + self.prevHash + '-' + str(self.time) + '-' + str(self.nonce))
		return hashlib.sha256(preHashData.encode()).hexdigest()	


	def mineBlock(self, difficulty):
		solveRequirement = ''.join(['0'] * difficulty)
		while self.hash[0:difficulty] != solveRequirement:
			self.nonce += 1
			self.hash = self.blockHash()


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
