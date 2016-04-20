import pex
from datetime import datetime, timedelta

Username = "postmatesapi"
Password = "Ea2eaJJf"
ClientID = "926bde1e"
ClientSecret = "fdfeb8d035128002d94d7b528090d44f"
Token = "b84c01366e964782a26391101f3a2a60"

client = pex.PEXAPIWrapper(token=Token)
# get_token
# resp = client.get_token(
#     client_id=ClientID,
#     client_secret=ClientSecret,
#     username=Username,
#     password=Password)


# Card/validate
# card_data = {"Cards": [{
#     "DateOfBirth": "07-18-1988",
#     "Email": "test@pm.com",
#     "FirstName": "Salar",
#     "LastName": unicode("Khan", "utf-8"),
#     "Phone": "1234567890",
#     "ProfileAddress": {
#         "State": unicode("CA", "utf-8")},
#     "ShippingAddress": {},
#     "ShippingMethod": "FirstClassMail",
#     "ShippingPhone": "1234567890"}]}
# resp = pex.PEXCardAPI.validate(card_data)


# Card/create
# card_data = {"Cards": [{
#     "DateOfBirth": "07-18-1988",
#     "Email": "lala@pm.com",
#     "FirstName": "Salar",
#     "LastName": unicode("Khan", "utf-8"),
#     "Phone": "1234567890",
#     "ProfileAddress": {
#         "State": unicode("CA", "utf-8")},
#     "ShippingAddress": {
#         "State": unicode("CA", "utf-8")},
#     "ShippingMethod": "FirstClassMail",
#     "ShippingPhone": "1234567890"}]}
# resp = client.create(card_data)

# u'{"CardOrderId":2875}'


# Card/activate
# card_id = 26132
# resp = client.activate(card_id=card_id)


# Card/get_order
# card_order_id = 2875
# resp = client.get_order(card_order_id=card_order_id)


# Card/block
# card_id = 26132
# resp = client.block(card_id=card_id)


# Card/activate
# card_id = 26132
# resp = client.unblock(card_id=card_id)


# Card/fund
# card_id = 26132
# resp = client.fund(card_id=card_id, amount=5)


# Details/get_account
# account_id = 26132
# resp = client.get_account(account_id=account_id)


# Details/get_all_accounts
# resp = client.get_all_accounts()


# Card/zero_balance
# card_id = 26132
# resp = client.zero_balance(card_id=card_id)


# Card/get_order
# card_order_id = 2875
# resp = client.get_order(card_order_id=card_order_id)


# Card/get_transaction_list
# now = datetime.utcnow().date()
# end = now + timedelta(days=5)
# start = now - timedelta(days=365)
# resp = client.get_transaction_list(
#     start_date=start,
#     end_date=end,
#     include_declines=True,
#     include_pendings=True
# )


# print resp