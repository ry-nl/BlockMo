from lib.blockchain import *
from time import time
import pprint

chain = BlockChain()
transactions = []

block = Block(transactions, time(), 0)
chain.addBlock(block)

block = Block(transactions, time(), 1)
chain.addBlock(block)

block = Block(transactions, time(), 2)
chain.addBlock(block)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(chain.encodeJSON())
print('length: ', len(chain.chain))