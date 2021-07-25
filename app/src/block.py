import hashlib

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