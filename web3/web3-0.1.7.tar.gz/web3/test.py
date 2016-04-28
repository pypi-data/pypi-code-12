from web3 import Web3, IPCProvider
w = Web3(IPCProvider(testnet=True))
w.config.defaultAccount = "0x3b63b366a72e5742B2aaa13a5e86725ED06a68f3"  # 
abi ="""
[ { "constant": true, "inputs": [], "name": "get", "outputs": [ { "name": "", "type": "int256", "value": "0", "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "v", "type": "int256" } ], "name": "set", "outputs": [], "type": "function" } ]
"""
c = w.eth.contract(abi)
ci = c.at("0x18AA120c207FA3909C73d15b9c7C97Ca7a8dDd8d")
print(ci)
print(ci.get())
print(ci.set(5))
print(w.fromWei(w.eth.getBalance(w.eth.getAccounts()[0]), "ether"))