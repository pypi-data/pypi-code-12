import Token

Provider = Token.ProviderService()
Bank = Token.BankService()

sk1, pk1 = Token.create_keypair()
sk2, pk2 = Token.create_keypair()

alice = Provider.create_member('alice', '123', pk1)
bob = Provider.create_member('bob', '123', pk2)


Token.set_context('bank-test', Token.keys["bank"])

access = Bank.create_access('alice', 'alice', 'test')
access2 = Bank.create_access('bob', 'bob', 'test')


Token.set_context(alice, sk1)
Provider.create_alias('ALICE'+pk1[:5])

alice_acc = Provider.create_account('test', access.id, "Personal Checking")
Provider.get_account(alice_acc.id)


Token.set_context(bob, sk2)
bob_acc = Provider.create_account('test', access2.id, "Merchant Business Account")
token = Provider.create_token('ALICE'+pk1[:5])

Token.set_context(alice, sk1)
Provider.endorse_token(token.id, alice_acc.id)


Token.set_context(bob, sk2)
payment = Provider.create_payment(token.id, bob_acc.id, 2, "EUR")

Token.set_context(alice, sk1)
Provider.get_account(alice_acc.id)
