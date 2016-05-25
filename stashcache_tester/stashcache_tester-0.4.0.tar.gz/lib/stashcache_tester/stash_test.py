#!/usr/bin/env python

import optparse
from stashcache_tester.StashCacheTester import StashCacheTester


def add_options(parser):
    parser.add_option("-c", "--config", dest="config", 
        help="Configuration file location", default="/etc/stashcache-tester/tester.conf")


def main():
    parser = optparse.OptionParser()
    add_options(parser)
    
    (options, args) = parser.parse_args()
    
    tester = StashCacheTester(options.config)
    
    if args[0] == "run":
        tester.runTests()
    elif args[0] == "reduce":
        tester.reduceResults()
    else:
        print "Error, no command or unrecognized command"
    




if __name__ == "__main__":
    main()
