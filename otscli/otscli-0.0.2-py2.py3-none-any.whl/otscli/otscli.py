#!/usr/bin/env python

import requests
# Disable HTTPS verification warnings.
from requests.packages import urllib3
urllib3.disable_warnings()
import argparse
import sys

def cli():
    parser = argparse.ArgumentParser(description='OTS console client')
    
    parser.add_argument('-d', nargs='?', default='https://pwd.rk.local', help='ots service url (default: https://pwd.rk.local)', metavar='url', dest='ots_url')
    parser.add_argument('-s', required=True, help='the secret value which is encrypted before being stored.', metavar='secret', dest='ots_secret')
    parser.add_argument('-p', required=False, help='a string that the recipient must know to view the secret.', metavar='passphrase', dest='ots_passphrase')
    
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()

def client():
    args = cli()
    ots_data = dict(secret=args.ots_secret)
    if args.ots_passphrase:
        ots_data.update({'passphrase':args.ots_passphrase})
    url = "{}/api/v1/share".format(args.ots_url)
    r = requests.post(url, data=ots_data, verify=False)
    print("{}/secret/{}" .format(args.ots_url, r.json()["secret_key"]))

if __name__ == "__main__":
    client()