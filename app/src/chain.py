from block import Block
from transaction import Transaction
from time import time
from Crypto.PublicKey import RSA

class BlockChain:
	def __init__(self):
		self.index = 1
		self.chain = [self.genesisBlock()]
		self.difficulty = 3
		self.unfulfilledTransactions = []
		self.miningReward = 20


	def genesisBlock(self):
		return Block(0, [], time())
		

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


	def getPrevBlock(self):
		return self.chain[-1]


	def addBlock(self, block):
		block.prevHash = self.getPrevBlock().hash
		block.mineBlock(self.difficulty)
		self.chain.append(block)


	def mineTransactions(self, rewardAddress):
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

		minerReward = Transaction('System', rewardAddress, self.miningReward)

		self.unfulfilledTransactions = [minerReward]


	def encodeJSON(self):
		chainJSON = []

		for block in self.chain:
			blockJSON = {}
			blockJSON['block hash'] = block.hash
			blockJSON['prev hash'] = block.prevHash
			blockJSON['transactions'] = block.transactions

			chainJSON.append(blockJSON)

		return chainJSON





