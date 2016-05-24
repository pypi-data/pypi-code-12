import Token
import time
import pytest

ProviderFIDOR = Token.ProviderService('fidor', env_arg="prod")
ProviderBBVA = Token.ProviderService('bbva', env_arg="prod")
BankFIDOR = Token.BankService('fidor', env_arg="prod")
BankBBVA = Token.BankService('bbva', env_arg="prod")


def test_basic():
    sk1, pk1 = Token.create_keypair()
    sk2, pk2 = Token.create_keypair()

    alice = ProviderFIDOR.create_member('alice', '123', pk1)
    bob = ProviderBBVA.create_member('bob', '123', pk2)

    assert alice.device is not None and alice.id is not None
    assert bob.device is not None and bob.id is not None


    Token.set_context('bank-fidor', Token.keys["bankFIDOR"])
    access = BankFIDOR.create_access('69568378', '69568378', 'fidor', session_id='alice')

    Token.set_context('bank-bbva', Token.keys["bankBBVA"])
    access2 = BankBBVA.create_access('93259302', '93259302', 'bbva', session_id='bob')

    assert access is not None
    assert access2 is not None


    Token.set_context(alice, sk1)
    ProviderFIDOR.create_alias('ALICE'+pk1[:5])

    alice_acc = ProviderFIDOR.create_account('fidor', access.id, "Personal Checking")
    assert alice_acc is not None

    account = ProviderFIDOR.get_account(alice_acc.id)
    alice_balance = float(account.balance.available.value)
    assert alice_balance > 0


    Token.set_context(bob, sk2)
    bob_acc = ProviderBBVA.create_account('bbva', access2.id, "Merchant Business Account")
    assert bob_acc is not None

    account = ProviderBBVA.get_account(bob_acc.id)
    bob_balance = float(account.balance.available.value)
    assert bob_balance > 0

    token = ProviderBBVA.create_token('ALICE'+pk1[:5])
    assert token.id is not None
    token_full = ProviderBBVA.get_token(token.id)
    assert token_full.state == 'Requested'

    Token.set_context(alice, sk1)
    token_full_alice = ProviderFIDOR.get_token(token.id)
    assert token_full_alice.state == 'Requested'
    ProviderFIDOR.endorse_token(token.id, alice_acc.id)
    token_full_alice_2 = ProviderFIDOR.get_token(token.id)
    assert token_full_alice_2.state == 'Endorsed'

    tokens = ProviderFIDOR.get_tokens()
    assert tokens is not None
    assert tokens.tokens is not None
    assert len(tokens.tokens) > 0

    Token.set_context(bob, sk2)
    payment = ProviderBBVA.create_payment(token.id, bob_acc.id, 0.03, "EUR", description="Test")
    assert payment is not None
    assert len(payment.id) > 0
    ProviderBBVA.create_alias('BOB'+pk2[:5])

    transactions_bob = ProviderBBVA.get_transactions(bob_acc.id).transactions
    assert len(transactions_bob) > 0

    Token.set_context(alice, sk1)
    transactions_alice = ProviderFIDOR.get_transactions(alice_acc.id).transactions
    assert len(transactions_alice) > 0

    Token.set_context(alice, sk1)
    token_new = ProviderFIDOR.create_token('BOB'+pk2[:5])
    Token.set_context(bob, sk2)
    ProviderBBVA.endorse_token(token_new.id, bob_acc.id)
    Token.set_context(alice, sk1)
    payment_new = ProviderFIDOR.create_payment(token_new.id, alice_acc.id, 0.03, "EUR", description="Test Refund")

    time.sleep(5)
    account_new = ProviderFIDOR.get_account(alice_acc.id)
    alice_balance_new = float(account_new.balance.available.value)
    assert alice_balance_new == alice_balance


def test_two_members():
    sk1, pk1 = Token.create_keypair()
    alice = ProviderFIDOR.create_member('alice', '123', pk1)

    sk1, pk1 = Token.create_keypair()
    alice = ProviderFIDOR.create_member('alice', '123', pk1)

def test_new_objects():
    global ProviderFIDOR
    global ProviderBBVA
    global BankFIDOR
    global BankBBVA

    ProviderFIDOR = Token.ProviderService('fidor', env_arg="prod")
    ProviderBBVA = Token.ProviderService('bbva', env_arg="prod")
    BankFIDOR = Token.BankService('fidor', env_arg="prod")
    BankBBVA = Token.BankService('bbva', env_arg="prod")

    sk1, pk1 = Token.create_keypair()
    alice = ProviderFIDOR.create_member('alice', '123', pk1)

    sk1, pk1 = Token.create_keypair()
    alice = ProviderFIDOR.create_member('alice', '123', pk1)
    test_basic()

def test_invalid_sig():
    sk1, pk1 = Token.create_keypair()
    sk2, pk2 = Token.create_keypair()

    alice = ProviderFIDOR.create_member('alice', '123', pk1)
    bob = ProviderBBVA.create_member('bob', '123', pk2)

    assert alice.device is not None and alice.id is not None
    assert bob.device is not None and bob.id is not None


    Token.set_context('bank-fidor', Token.keys["bankFIDOR"])
    access = BankFIDOR.create_access('69568378', '69568378', 'fidor', session_id='alice')

    Token.set_context('bank-bbva', Token.keys["bankBBVA"])
    access2 = BankBBVA.create_access('93259302', '93259302', 'bbva', session_id='bob')

    assert access is not None
    assert access2 is not None


    Token.set_context(alice, sk2)

    with pytest.raises(Token.rest.ApiException):
        ProviderFIDOR.create_alias('ALICE'+pk1[:5])
