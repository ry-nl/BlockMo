from lib.blockchain import *
from time import time
import pprint

chain = BlockChain()

key1 = chain.generateKeys()
key2 = chain.generateKeys()
print(key1)

chain.makeTransaction('Ryan', 'Edward', 20, key1, key1)
chain.makeTransaction('Edward', 'Ryan', 10, key1, key1)
chain.makeTransaction('Edward', 'Ryan', 30, key1, key1)

chain.mineTransactions()

chain.makeTransaction('Ryan', 'Edward', 30, key1, key1)
chain.makeTransaction('Edward', 'Ryan', 10, key2, key2)

chain.mineTransactions()

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(chain.encodeJSON())
print('length: ', len(chain.chain))