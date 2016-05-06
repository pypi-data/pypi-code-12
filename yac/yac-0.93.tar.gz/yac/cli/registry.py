import argparse, json, os
from yac.lib.variables import get_variable, set_variable
from yac.lib.registry import set_private_registry, get_private_registry, clear_private_registry


def main():

    parser = argparse.ArgumentParser('Manage my yac registry')

    # optional args
    parser.add_argument('--set',      help='yac will prompt your for the connection params for a private registry',
                                      action='store_true')
    parser.add_argument('--show',     help='show the registry currently configured',
                                      action='store_true')
    parser.add_argument('--clear',    help='clear the private registry currently configured')    
    
    args = parser.parse_args()       

    if args.set:

        redis_host = raw_input("Please input the name of the Redis host you would like to use for your yac private registry >> ")

        redis_port = raw_input("Please input the port the Redis host listens on >> ")
        private_registry = {"host": redis_host, "port": redis_port}

        set_private_registry(private_registry)

    if args.show:

        private_registry = get_private_registry()

        if private_registry:
            print json.dumps(private_registry, indent=4)
        else:
            print "No private registry is currently configured"

    if args.clear:

        print "Clearing private registry preferences currently in place"
        raw_input("Hit Enter to continue >> ")
        clear_private_registry()            

