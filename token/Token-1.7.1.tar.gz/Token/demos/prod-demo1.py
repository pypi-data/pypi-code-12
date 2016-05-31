import Token

Provider1 = Token.ProviderService(Token.providers[0])
Provider2 = Token.ProviderService(Token.providers[1])
Bank1 = Token.BankService(Token.banks[0])
Bank2 = Token.BankService(Token.banks[1])

sk1, pk1 = Token.create_keypair()
sk2, pk2 = Token.create_keypair()

alice = Provider1.create_member('aliceDevice', '123', pk1)
bob = Provider2.create_member('bobDevice', '123', pk2)

Token.set_context('bank-'+Token.banks[0], Token.keys["bank1"])
access = Bank1.create_access(Token.clients[0], Token.accounts[0], pk1)
Token.set_context(alice, sk1)
alice_acc = Provider1.create_account(Token.banks[0], access.id, "Personal Checking")

Token.set_context('bank-'+Token.banks[1], Token.keys["bank2"])
access2 = Bank2.create_access(Token.clients[1], Token.accounts[1], pk2)
Token.set_context(bob, sk2)
bob_acc = Provider2.create_account(Token.banks[1], access2.id, "Merchant Business Account")

Token.set_context(alice, sk1)
Provider1.create_alias('ALICE'+pk1[:5])
Provider1.get_account(alice_acc.id)

Token.set_context(bob, sk2)
token = Provider2.create_token('ALICE'+pk1[:5])

Token.set_context(alice, sk1)
Provider1.get_tokens()
Provider1.endorse_token(token.id, alice_acc.id)

Token.set_context(bob, sk2)
payment = Provider2.create_payment(token.id, bob_acc.id, 1, "EUR",
                                      description="Order 5672, Bob's transaction")

Token.set_context(alice, sk1)
Provider1.get_account(alice_acc.id)
