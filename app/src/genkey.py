from Crypto.PublicKey import RSA

def genKey():
	key = RSA.generate(2048)
	private_key = key.export_key()
	file_out = open("private1.pem", "wb")
	file_out.write(private_key)
	file_out.close()

	public_key = key.publickey().export_key()
	file_out = open("public1.pem", "wb")
	file_out.write(public_key)
	file_out.close()

	return public_key