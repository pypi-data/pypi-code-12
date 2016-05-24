# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from btctxstore.services.interface import BlockchainService


class Bitcoind(BlockchainService):

    def get_tx(self, txid):
        pass  # ez

    def confirms(self, txid):
        pass  # should be ok!

    def send_tx(self, tx):
        pass  # ez

    def spendables_for_address(self, bitcoin_address):
        pass
        # possible with patched bitcoind, addrindex
        # https://github.com/btcdrak/bitcoin/releases
        # also see https://github.com/bitcoin/bitcoin/pull/5048
