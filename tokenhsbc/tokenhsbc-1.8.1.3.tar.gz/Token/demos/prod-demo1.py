import Token

provider1 = Token.provider('config/prd-provider-blue.json')
provider2 = Token.provider('config/prd-provider-green.json')
bank1 = Token.bank('config/prd-bank-blue.json')
bank2 = Token.bank('config/prd-bank-green.json')

alice = provider1.create_member('aliceDevice', '123')
alice_access = bank1.create_access('alice', 'checking1', alice.pk)
alice_account = provider1.create_account(alice, bank1, alice_access.id, "Personal Checking")

bob = provider2.create_member('bobDevice', '123')
bob_access = bank2.create_access('bob', 'checking2', bob.pk)
bob_account = provider2.create_account(bob, bank2, bob_access.id, "Merchant Business Account")

alice_alias = 'ALICE' + alice.pk[:5]
provider1.create_alias(alice, alice_alias)
provider1.get_account(alice, alice_account.id)
token = provider2.create_token(bob, alice_alias, terms={"currency": "USD"})

provider1.get_tokens(alice, 0, 100)
provider1.endorse_token(alice, token.id, alice_account.id)

payment = provider2.create_payment(bob, token.id, bob_account.id, 1, "EUR", description="Order 5672, Bob's transaction")
account = provider1.get_account(alice, alice_account.id)

