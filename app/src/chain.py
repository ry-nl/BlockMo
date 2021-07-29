from .block import *
from .transaction import *
from time import time
import pickle
from Crypto.PublicKey import RSA

class BlockChain:
	def __init__(self):
		self.chain = [self.genesisBlock()]
		self.difficulty = 3
		self.unfulfilledTransactions = []
		self.miningReward = 20


	def genesisBlock(self):
		return Block(0, [], time())
		

	def makeTransaction(self, key, senderKey, recipientKey, amount):
		if not senderKey or not recipientKey or not amount:
			return False

		senderKey_encoded = senderKey.export_key('PEM')
		recipientKey_encoded = recipientKey.export_key('PEM')

		transaction = Transaction(senderKey_encoded, recipientKey_encoded, amount)
		transaction.signTransaction(key)

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


	def isValid(self):
		for block in self.chain:
			if not block.isValid():
				return False

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

