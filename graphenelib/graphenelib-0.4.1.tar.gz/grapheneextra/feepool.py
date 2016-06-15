from grapheneapi.grapheneclient import GrapheneClient
from graphenebase import transactions
from graphenebase.account import PrivateKey
from datetime import datetime
import time
import math


    elif self.config.wif:
        account = self.ws.get_account(self.config.account)
        s = {"fee": {"amount": 0, "asset_id": "1.3.0"},
             "seller": account["id"],
             "amount_to_sell": {"amount": int(amount * rate * 10 ** base["precision"]),
                                "asset_id": base["id"]
                                },
             "min_to_receive": {"amount": int(amount * 10 ** quote["precision"]),
                                "asset_id": quote["id"]
                                },
             "expiration": transactions.formatTimeFromNow(expiration),
             "fill_or_kill": killfill,
             }
        ops = [transactions.Operation(transactions.Limit_order_create(**s))]
        expiration = transactions.formatTimeFromNow(30)
        ops = transactions.addRequiredFees(self.ws, ops, "1.3.0")
        ref_block_num, ref_block_prefix = transactions.getBlockParams(self.ws)
        transaction = transactions.Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        transaction = transaction.sign([self.config.wif], self.prefix)
        transaction     = transactions.JsonObj(transaction)
        if not (self.safe_mode or self.propose_only):
            self.ws.broadcast_transaction(transaction, api="network_broadcast")
    else:
        raise NoWalletException()
