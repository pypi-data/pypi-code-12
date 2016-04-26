from Crypto.PublicKey import RSA
public_key = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCntbY8dJ+MMGSmuR+bLHs2Zj2L\nKm77oT83i3RNuUj8G5+sPMLe8oaS4efz19S7puVR9bpCfkeplROrckx1//LUn3qW\nTTBYF7ZTYar3aiNuEodG9wO277e1Om3cwgpi9FvWVFjAYhmVoNNctKQBTsEfpd7M\n6ZR1jDCnhDQLApHiWwIDAQAB\n-----END PUBLIC KEY-----'
# file for encrypting the user password for safe storage
def create_enc_password(password):
	pubkey = RSA.importKey(public_key)
	return pubkey.encrypt(password, None)