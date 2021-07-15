from lib.blockchain import *
from time import time
import pprint

chain = BlockChain()
transactions = []

block = Block(1, transactions, time())
chain.addBlock(block)

block = Block(2, transactions, time())
chain.addBlock(block)

block = Block(3, transactions, time())
chain.addBlock(block)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(chain.encodeJSON())
print('length: ', len(chain.chain))