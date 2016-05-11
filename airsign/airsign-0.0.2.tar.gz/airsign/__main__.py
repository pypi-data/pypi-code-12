#!/usr/bin/env python3

import sys
import os
import argparse
from grapheneapi.graphenewsrpc import GrapheneWebsocketRPC
from pprint import pprint
from graphenebase.account import PrivateKey, PublicKey, Address
import graphenebase.transactions as transactions
from graphenebase import memo
from airsign.wallet import Wallet
from airsign.configuration import Configuration
from prettytable import PrettyTable


def broadcastTx(tx):
    if isinstance(tx, transactions.Signed_Transaction):
        tx     = transactions.JsonObj(tx)
    return rpc.broadcast_transaction(tx, api="network_broadcast")


def executeOps(ops, wifs=None):
    if any([not w for w in wifs]):
        print("Missing required key")
        return

    expiration = transactions.formatTimeFromNow(30)
    ops = transactions.addRequiredFees(rpc, ops, "1.3.0")
    ref_block_num, ref_block_prefix = transactions.getBlockParams(rpc)
    tx     = transactions.Signed_Transaction(
        ref_block_num=ref_block_num,
        ref_block_prefix=ref_block_prefix,
        expiration=expiration,
        operations=ops
    )
    tx = tx.sign(wifs, "BTS")

    pprint(transactions.JsonObj(tx))

    if not args.nobroadcast:
        reply = broadcastTx(tx)
        if reply:
            print(reply)
    else:
        print("Not broadcasting anything!")
        reply = None


def main() :
    global args
    global rpc
    config = Configuration()

    if "node" not in config or not config["node"]:
        config["node"] = "wss://bitshares.openledger.info/ws"

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Command line tool to interact with the BitShares network"
    )

    """
        Default settings for all tools
    """
    parser.add_argument(
        '--node',
        type=str,
        default=config["node"],
        help='Websocket URL for public BitShares API (default: "wss://bitshares.openledger.info/ws")'
    )
    parser.add_argument(
        '--rpcuser',
        type=str,
        default=config["rpcuser"],
        help='Websocket user if authentication is required'
    )
    parser.add_argument(
        '--rpcpassword',
        type=str,
        default=config["rpcpassword"],
        help='Websocket password if authentication is required'
    )
    parser.add_argument(
        '--nobroadcast',
        action='store_true',
        help='Do not broadcast anything'
    )
    subparsers = parser.add_subparsers(help='sub-command help')
    parser.set_defaults(command=None)

    """
        Command "set"
    """
    setconfig = subparsers.add_parser('set', help='Set configuration')
    setconfig.add_argument(
        'key',
        type=str,
        choices=["node",
                 "rpcuser",
                 "rpcpassword",
                 "account"
                 ],
        help='Configuration key'
    )
    setconfig.add_argument(
        'value',
        type=str,
        help='Configuration value'
    )
    setconfig.set_defaults(command="set")

    """
        Command "addkey"
    """
    addkey = subparsers.add_parser('addkey', help='Add a new key to the wallet')
    addkey.add_argument(
        'wifkeys',
        nargs='*',
        type=str,
        help='the private key in wallet import format (wif)'
    )
    addkey.set_defaults(command="addkey")

    """
        Command "listkeys"
    """
    listkeys = subparsers.add_parser('listkeys', help='List available keys in your wallet')
    listkeys.set_defaults(command="listkeys")

    """
        Command "listaccounts"
    """
    listaccounts = subparsers.add_parser('listaccounts', help='List available accounts in your wallet')
    listaccounts.set_defaults(command="listaccounts")

    """
        Command "getbalance"
    """
    getbalance = subparsers.add_parser('getbalance', help='Get balances of available account(s)')
    getbalance.set_defaults(command="getbalance")
    getbalance.add_argument(
        'account',
        type=str,
        nargs="*",
        default=[config["account"]],
        help='Accounts for which to retrieve the balance',
    )

    """
        Command "transfer"
    """
    transfer = subparsers.add_parser('transfer', help='Transfer funds from your wallet to someone else')
    transfer.set_defaults(command="transfer")
    transfer.add_argument(
        '--from',
        type=str,
        help='Transfer from this account',
        default=config["account"],
    )
    transfer.add_argument(
        '--to',
        type=str,
        help='Transfer to this account',
        required=True,
    )
    transfer.add_argument(
        '--amount',
        type=str,
        help='Transfer this amount (format: "amount SYMBOL")',
        action="append",
        required=True,
    )
    transfer.add_argument(
        '--memo',
        default='',
        type=str,
        help='Memo',
    )

    """
        Command "approve"
    """
    approve = subparsers.add_parser('approve', help='approve funds from your wallet to someone else')
    approve.set_defaults(command="approve")
    approve.add_argument(
        '--account',
        type=str,
        help='Approve with this account',
        default=config["account"],
    )
    approve.add_argument(
        'proposal',
        type=str,
        help='Proposal to approve',
    )

    """
        Parse Arguments
    """
    args = parser.parse_args()

    rpc_not_required = ["set", ""]
    if args.command not in rpc_not_required and args.command:
        rpc = GrapheneWebsocketRPC(args.node, args.rpcuser, args.rpcpassword)

    if args.command == "set":
        config[args.key] = args.value

    elif args.command == "addkey":
        wallet = Wallet(rpc)
        if len(args.wifkeys):
            for wifkey in args.wifkeys:
                pub = (wallet.addPrivateKey(wifkey))
                if pub:
                    print(pub)
        else:
            import getpass
            wifkey = ""
            while True:
                wifkey = getpass.getpass('Private Key (wif) [Enter to quit]:')
                if not wifkey:
                    break
                pub = (wallet.addPrivateKey(wifkey))
                if pub:
                    print(pub)

    elif args.command == "listkeys":
        t = PrettyTable(["Available Key"])
        t.align = "l"
        for key in Wallet(rpc).getPublicKeys():
            t.add_row([key])
        print(t)

    elif args.command == "listaccounts":
        t = PrettyTable(["Name", "Available Key"])
        t.align = "l"
        for account in Wallet(rpc).getAccounts():
            t.add_row(account)
        print(t)

    elif args.command == "getbalance":
        if args.account:
            accounts = [a for a in args.account]
        else:
            accounts = [a[0] for a in Wallet(rpc).getAccounts()]

        for account_name in accounts:
            account = rpc.get_account(account_name)
            t = PrettyTable(["Amount", "Asset"])
            t.align = "l"
            balances = rpc.get_account_balances(account["id"], [])
            if not balances:
                continue
            print(account["name"] + ":")
            for balance in balances:
                asset = rpc.get_objects([balance["asset_id"]])[0]
                amount = int(balance["amount"]) / 10 ** asset["precision"]
                if amount:
                    t.add_row([amount, asset["symbol"]])
            print(t)

    elif args.command == "transfer":
        wallet = Wallet(rpc)

        ops = []
        for amountStr in args.amount:
            amount, symbol = amountStr.split(" ")
            amount = float(amount)
            asset = rpc.get_asset(symbol)
            from_account = rpc.get_account(getattr(args, "from"))
            to_account = rpc.get_account(getattr(args, "to"))

            transferObj = {
                "fee": {"amount": 0,
                        "asset_id": "1.3.0"
                        },
                "from": from_account["id"],
                "to": to_account["id"],
                "amount": {"amount": int(amount * 10 ** asset["precision"]),
                           "asset_id": asset["id"]
                           }
            }

            if args.memo:
                memo_key = wallet.getMemoKeyForAccount(getattr(args, "from"))
                if not memo_key:
                    print("Missing memo private key!")
                    return

                import random
                nonce = str(random.getrandbits(64))
                encrypted_memo = memo.encode_memo(PrivateKey(memo_key),
                                                  PublicKey(to_account["options"]["memo_key"]),
                                                  nonce,
                                                  args.memo)
                memoStruct = {"from": from_account["options"]["memo_key"],
                              "to": to_account["options"]["memo_key"],
                              "nonce": nonce,
                              "message": encrypted_memo,
                              "chain": "BTS"}
                transferObj["memo"] = transactions.Memo(**memoStruct)

            transfer = transactions.Transfer(**transferObj)
            ops.append(transactions.Operation(transfer))

        wif = wallet.getActiveKeyForAccount(getattr(args, "from"))
        executeOps(ops, [wif])

    elif args.command == "approve":
        wallet = Wallet(rpc)
        account = rpc.get_account(args.account)
        s = {'fee_paying_account': account["id"],
             'proposal': args.proposal,
             'active_approvals_to_add': [account["id"]],
             "fee": transactions.Asset(amount=0, asset_id="1.3.0"),
             }
        op = transactions.Proposal_update(**s)
        wif = wallet.getActiveKeyForAccount(args.account)
        executeOps([transactions.Operation(op)], [wif])

    else:
        print("No valid command given")


rpc = None
args = None
if __name__ == '__main__':
    main()
