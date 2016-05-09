import Token

ProviderFIDOR = Token.ProviderService('fidor')
ProviderBBVA = Token.ProviderService('bbva')
BankFIDOR = Token.BankService('fidor')
BankBBVA = Token.BankService('bbva')

sk1, pk1 = Token.create_keypair()
sk2, pk2 = Token.create_keypair()

alice = ProviderFIDOR.create_member('alice', '123', pk1)
bob = ProviderBBVA.create_member('bob', '456', pk2)

Token.set_context('bank-fidor', Token.keys["bankFIDOR"])
alice_access = BankFIDOR.create_access('69568378', '69568378', 'fidor', session_id='alice')

Token.set_context('bank-bbva', Token.keys["bankBBVA"])
bob_access = BankBBVA.create_access('93259302', '93259302', 'bbva', session_id='bob')


Token.set_context(alice, sk1)
ProviderFIDOR.create_alias('ALICE'+pk1[:5])

alice_acc = ProviderFIDOR.create_account('fidor', alice_access.id, "Personal Checking")
ProviderFIDOR.get_account(alice_acc.id)

Token.set_context(bob, sk2)
bob_acc = ProviderBBVA.create_account('bbva', bob_access.id, "Merchant Business Account")
token = ProviderBBVA.create_token('ALICE'+pk1[:5])

Token.set_context(alice, sk1)
ProviderFIDOR.get_tokens()
ProviderFIDOR.endorse_token(token.id, alice_acc.id)


Token.set_context(bob, sk2)
payment = ProviderBBVA.create_payment(token.id, bob_acc.id, 0.02, "EUR", description="Order 5672, Bob ")

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
