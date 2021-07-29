from Crypto.PublicKey import RSA

def genKey(username):
	key = RSA.generate(2048)

	private_key = key.export_key()
	file_out = open(f"app/wallets/{username}private.pem", "wb")
	file_out.write(private_key)
	file_out.close()

	public_key = key.publickey().export_key()
	file_out = open(f"app/wallets/{username}public.pem", "wb")
	file_out.write(public_key)
	file_out.close()

	return public_key