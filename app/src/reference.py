from Crypto.PublicKey import RSA

# def genKey():
key = RSA.generate(2048)
private_key = key.export_key(passphrase='123')
# file_out = open("private1.pem", "wb")
# file_out.write(private_key)
# file_out.close()

public_key = key.publickey().export_key()
# file_out = open("public1.pem", "wb")
# file_out.write(public_key)
# file_out.close()

ret_private_key = RSA.import_key(private_key.decode(), '123')

print(type(ret_private_key))
print(ret_private_key)
if ret_private_key == key:
	print('same')

# return public_key