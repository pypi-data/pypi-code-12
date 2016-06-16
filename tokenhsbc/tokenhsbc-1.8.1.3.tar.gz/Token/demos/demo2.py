import Token

providerFIDOR = Token.provider('config/dev-provider-fidor.json')
providerBBVA = Token.provider('config/dev-provider-bbva.json')
bankFIDOR = Token.bank('config/dev-bank-fidor.json')
bankBBVA = Token.bank('config/dev-bank-bbva.json')

# Create alice member and link it to the alice's bank account.
alice_alias = 'ALICE' + Token.generate_id(10)
alice = Token.create_member(providerFIDOR, alice_alias, 'aliceDevice', '123')
alice_access = bankFIDOR.create_access('alice', 'checking1', alice.public_key())
alice_account = alice.link_account(bankFIDOR.bank_code(), alice_access, "Alice's checking")

# Create bob member and link it to the bob's bank account.
bob_alias = 'BOB' + Token.generate_id(10)
bob = Token.create_member(providerBBVA, bob_alias, 'bobDevice', '321')
bob_access = bankBBVA.create_access('bob', 'checking2', bob.public_key())
bob_account = bob.link_account(bankBBVA.bank_code(), bob_access, "Bob's checking")

# Bob sends money to Alice.
token = bob_account.transfer_money(alice_alias, 15, 'EUR', description='Thanks for the dinner')

# Alice gets the token and creates payment.
alice_account.charge_token(token, 15, 'EUR')
