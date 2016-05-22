# -*- coding: utf-8 -*-
# -----------------------
# Copyright 2015 Halfmoon Labs, Inc.
# All Rights Reserved
# -----------------------

'''
    local configuration file
'''

import os

DEBUG = True

#BLOCKSTORED_IP = '172.30.1.174'

email_regrex = '@yopmail.com'

MAIN_SERVER = 'localhost'
LOAD_SERVERS = []
MAX_PENDING_TX = 50

IGNORE_USERNAMES = ['muneeb', 'leena', 'chord', 'onename', 'blockstack', 'jp', 'to',
                    'usv', 'ycombinator', 'svangel', 'highline', 'openchain', 'contact', 'webmaster', 'user', 'ghandi']

DHT_IGNORE = ['thetodfather.id', 'hsingh.id']

IGNORE_NAMES_STARTING_WITH = ['clone_']

UTXO_SERVER = '52.21.61.40'
UTXO_USER = 'halfmoon4534t4csdv3ry3rtwcdsv2t'
UTXO_PASSWD = 'gfdhknr2gn34trdgve4g3vcv29evxcvcfhgnnsvsnstotalcare4353tfish'

CONSENSUS_SERVERS = ['172.30.1.174', 'blockstore.blockstack.org', '172.30.1.189']
