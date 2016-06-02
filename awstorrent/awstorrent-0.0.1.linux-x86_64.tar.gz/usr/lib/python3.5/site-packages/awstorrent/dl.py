#!/usr/bin/python

from __init__ import download
import pyperclip
import argparse
# Address of my amazon-web-service downloading server 
aws="firearasi@52.53.224.102"

# use transmission [torrent file address]
parser=argparse.ArgumentParser(prog="My torrent downloader \
    through aws",prefix_chars='-')
parser.add_argument('torrent', help='torrent address',nargs='?',
    default=pyperclip.paste())
parser.add_argument('-o','--output_dir', default='.',
    help='set local destination dir')
parser.add_argument('-t','--title', help='directory title')
parser.add_argument('-k','--keep_in_aws',
    action='store_true',help='keep file in aws server')
args=parser.parse_args()


download(aws,args.torrent,args.title,args.output_dir,args.keep_in_aws)
  








download(aws,torrent,args.title,args.output_dir)


