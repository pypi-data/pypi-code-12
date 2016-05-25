from Crypto.Cipher import AES
import base64
import os

class Endecrypt :

	def encryption(privateInfo):
		BLOCK_SIZE = 16
		PADDING = '{'
		pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
		EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
		secret = os.urandom(BLOCK_SIZE)
		print 'encryption key:',secret
		cipher = AES.new(secret)
		encoded = EncodeAES(cipher, privateInfo)
		print 'Encrypted string:', encoded   

	def decryption(encryptedString):
		PADDING = '{'
		DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
		encryption = encryptedString
		key = ''
		cipher = AES.new(key)
		decoded = DecodeAES(cipher, encryption)
		print decoded
 
