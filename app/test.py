from src.chain import *
from time import time
import pprint

chain = BlockChain()

priv_ryan = RSA.import_key(open('private.pem').read())
pub_ryan = RSA.import_key(open('public.pem').read())

priv_ed = RSA.import_key(open('private1.pem').read())
pub_ed = RSA.import_key(open('public1.pem').read())

chain.makeTransaction(priv_ryan, pub_ryan, pub_ed, 10)
chain.makeTransaction(priv_ed, pub_ed, pub_ryan, 10)

chain.mineTransactions(pub_ryan)

chain.makeTransaction(priv_ryan, pub_ryan, pub_ed, 10)
chain.makeTransaction(priv_ed, pub_ed, pub_ryan, 10)
chain.makeTransaction(priv_ryan, pub_ryan, pub_ed, 10)

chain.mineTransactions(pub_ryan)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(chain.encodeJSON())
print('length: ', len(chain.chain))

print(chain.isValid())
print(chain.unfulfilledTransactions)