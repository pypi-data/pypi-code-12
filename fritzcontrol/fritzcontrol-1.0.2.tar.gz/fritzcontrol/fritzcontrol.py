#!/usr/bin/env python
from lib import FritzControl
import argparse


def setWifiPswd(args):
    print "Setting wifi password"
    if args.config:
        fC = FritzControl(conf=args.config)
    else:
        fC = FritzControl(url=args.address, user=args.user, password=args.password)

    fC.setWifiPassword(args.password)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="config path")
parser.add_argument("-u", "--user", help="username")
parser.add_argument("-a", "--address", help="URL/Address (https)")
parser.add_argument("-p", "--password", help="password")

subparsers = parser.add_subparsers(title="Command", help="FritzControl command you want to run")

parser_setwifipassword = subparsers.add_parser('setWifiPassword', help='sets wifi password')
parser_setwifipassword.add_argument('password')
parser_setwifipassword.set_defaults(func=setWifiPswd)
args = parser.parse_args()
args.func(args)
