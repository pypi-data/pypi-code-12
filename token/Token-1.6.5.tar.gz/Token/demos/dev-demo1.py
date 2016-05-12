import Token

ProviderFIDOR = Token.ProviderService('fidor')
ProviderBBVA = Token.ProviderService('bbva')
BankFIDOR = Token.BankService('fidor')
BankBBVA = Token.BankService('bbva')

sk1, pk1 = Token.create_keypair()
sk2, pk2 = Token.create_keypair()

alice = ProviderFIDOR.create_member('alice', '123', pk1)
bob = ProviderBBVA.create_member('bob', '123', pk2)

Token.set_context('bank-fidor', Token.keys["bankFIDOR"])
access = BankFIDOR.create_access('1008', '1008', 'fidor', session_id='test')

Token.set_context('bank-bbva', Token.keys["bankBBVA"])
access2 = BankBBVA.create_access('1008', '1008', 'bbva', session_id='test')


Token.set_context(alice, sk1)
ProviderFIDOR.create_alias('ALICE'+pk1[:5])

alice_acc = ProviderFIDOR.create_account('fidor', access.id, "Personal Checking")
ProviderFIDOR.get_account(alice_acc.id)

Token.set_context(bob, sk2)
bob_acc = ProviderBBVA.create_account('bbva', access2.id, "Merchant Business Account")
token = ProviderBBVA.create_token('ALICE'+pk1[:5])

Token.set_context(alice, sk1)
ProviderFIDOR.get_tokens()
ProviderFIDOR.endorse_token(token.id, alice_acc.id)


Token.set_context(bob, sk2)
payment = ProviderBBVA.create_payment(token.id, bob_acc.id, 0.02, "EUR", description="Order 5672, Bob's transaction")

Token.set_context(alice, sk1)
ProviderFIDOR.get_account(alice_acc.id)


# Return the money by creating a Token in the reverse direction
Token.set_context(bob, sk2)
ProviderBBVA.create_alias('BOB'+pk2[:5])

Token.set_context(alice, sk1)
token2 = ProviderFIDOR.create_token('BOB'+pk2[:5])

Token.set_context(bob, sk2)
ProviderBBVA.endorse_token(token2.id, bob_acc.id)

Token.set_context(alice, sk1)
payment = ProviderFIDOR.create_payment(token2.id, alice_acc.id, 0.02, "EUR", description="Order 5672, Bob refund")
ProviderFIDOR.get_account(alice_acc.id)
