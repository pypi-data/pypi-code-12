#!/usr/bin/python

import pyperclip
import argparse
from . import download
# Address of my amazon-web-service downloading server 

def main(): 
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

if __name__=='__main__':
    main()











