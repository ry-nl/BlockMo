from app.block import *
from app.transaction import *
from time import time
from urllib.parse import urlparse
import requests

class BlockChain:
	def __init__(self):
		self.chain = [self.genesisBlock()]
		self.unfulfilledTransactions = []
		self.difficulty = 3
		self.miningReward = 20
		self.nodes = set()
		print('INIT')


	def genesisBlock(self):
		return Block(0, [], time())
		

	def makeTransaction(self, key, sender, senderKey, recipient, recipientKey, amount):
		if not senderKey or not recipientKey or not amount:
			return False

		senderKey_encoded = senderKey.export_key('PEM')
		recipientKey_encoded = recipientKey.export_key('PEM')

		transaction = Transaction(sender, senderKey_encoded, recipient, recipientKey_encoded, amount)
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


	def mineTransactions(self, recipient, rewardAddress):
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

		minerReward = Transaction('System', 'Mining Reward', recipient, rewardAddress, self.miningReward)

		self.unfulfilledTransactions = [minerReward]

		return True


	def isValid(self):
		for block in self.chain:
			if not block.isValid():
				return False

		return True
		

	def createNode(self, address):
		url = urlparse(address)
		print(url.netloc)
		self.nodes.add(url.netloc)


	def createConsensus(self):
		allNodes = self.nodes
		assertLength = len(self.chain)
		assertChain = None

		print(allNodes)

		for node in allNodes:
			response = requests.get(f'http://{node}/chain/info')
			if response.status_code == 200:
				otherLength = response.json()['length']
				otherChain = response.json()['chain']

				if assertLength < otherLength:
						assertChain = self.decodeJSON(otherChain)
						assertLength = otherLength

		if assertChain:
			self.chain = self.decodeJSON(assertChain)
			print(self.chain)
			return True
		
		print('FALSE')
		return False


	def getUserBalance(self, username):
		balance = 50
		for block in self.chain:
			try:
				for transaction in block.transactions:
					if transaction.sender == username:
						balance -= transaction.amount
					elif transaction.recipient == username:
						balance += transaction.amount
			except:
				pass	
			
		return balance
	

	def encodeJSON(self):
		chainJSON = []

		for block in self.chain:
			blockJSON = {}
			blockJSON['block hash'] = block.hash
			blockJSON['prev hash'] = block.prevHash
			blockJSON['transactions'] = block.transactions

			chainJSON.append(blockJSON)

		return chainJSON

	def decodeJSON(self, chainJSON):
			chain = []

			for blockJSON in chainJSON:
				transactions = []

				for transactionJSON in blockJSON['transactions']:
					transaction = Transaction(transactionJSON['sender'], transactionJSON['fromAddress'], transactionJSON['reciever'], transactionJSON['toAddress'], transactionJSON['amount'])
					transaction.time = transactionJSON['time']
					transaction.hash = transactionJSON['hash']
					transaction.SHAhash = transactionJSON['SHAhash']
					transactions.append(transaction)

				block = Block(blockJSON['id'], transactions, blockJSON['time']);
				block.hash = blockJSON['hash'];
				block.prevHash =blockJSON['prevHash'];
				block.nonce = blockJSON['nonce'];

				chain.append(block);

			return chain;