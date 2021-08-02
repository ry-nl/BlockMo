# **BlockChain Venmo**
______________________________________

This is a project intended to demonstrate a peer to peer, decentralized, python-based cryptocurrency exchange platform. Created with Flask and SQLAlchemy
SHA hashed and RSA encrypted

main1.py and main2.py are intended to recreate 2 users running separate instances of the site. Either can be run directly via python main1.py or python main2.py.

When creating a new user, you will be asked to input an email authentication key. You will be able to retrieve this key from the inbox of the inputted email address. After creating an account, a pair of randomly generated private and public keys will be placed in the BlockMo/app/wallets directory. Please do not rename, move, or modify these files in any way, as doing so will invalidate any transactions you make and receive.

The blockchain object data is not stored between runs for ease of testing, but user data is kept in an SQLAlchemy database.

Please install all the dependencies needed before running this program!

Thank you! :)

**NOTE**
Before running, please create a directory called 'wallets' under BlockMo/app/
This directory will be used to store the public and private keys associated with each account
