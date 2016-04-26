import Token

Provider = Token.ProviderService()
Bank = Token.BankService()

sk1, pk1 = Token.create_keypair()
sk2, pk2 = Token.create_keypair()

request = {'device': {'name':'alice', 'pushNotificationId':'123', \
    'publicKeys':[pk1]}}
request2 = {'device': {'name':'bob', 'pushNotificationId':'123', \
    'publicKeys':[pk2]}}
alice = Provider.create_member(request)
bob = Provider.create_member(request2)


Token.set_context('bank-test', Token.keys["bank"])
request = {
  'sessionId': '',
  'providerCode': 'test',
}
access = Bank.create_access('alice', 'alice', request)
access2 = Bank.create_access('bob', 'bob', request)


Token.set_context(alice, sk1)
Provider.create_alias('alice'+pk1[:5], {'description':''})
request = {
  "bankCode": "test",
  "accessId": access.id,
  "name": "Personal Checking"
}
alice_acc = Provider.create_account(request)
Provider.get_account(alice_acc.id)


Token.set_context(bob, sk2)
request = {
  "bankCode": "test"    ,
  "accessId": access2.id,
  "name": "Merchant Business Account"
}
bob_acc = Provider.create_account(request)
request = {
  "payerAliasCode": 'alice'+pk1[:5],
  "description": "",
  "terms": ""
}
token = Provider.create_token(request)


Token.set_context(alice, sk1)
Provider.endorse_token(token.id, {"accountId":alice_acc.id})


Token.set_context(bob, sk2)
request = {
  "accountId": bob_acc.id,
  "description": "",
  "amount": {
    "value": "5",
    "unit": "EUR"
  },
  "protocol": "",
  "destination": ""
}
payment = Provider.create_payment(token.id, request)

Token.set_context(alice, sk1)
Provider.get_account(alice_acc.id)
