#!/usr/bin/env python

import argparse, sys, json, os

from yac.lib.registry import RegError
from yac.lib.params import validate_service_params, register_service_params, clear_service_params, get_service_params_by_name
from yac.lib.params import get_service_params_from_file, get_all_service_params_names, NULL_PARAMS

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('Install a set of service params in the yac registry')
    group = parser.add_argument_group()
    group.add_argument('--share', 
                        help=('register a set  of service params with the yac registry so they can be easily consumed by others.' +
                        ' (arg is the path to the params file)'),
                        type=lambda x: is_valid_file(parser, x))
    group.add_argument('--ver',  help='the version label to associate with this set of params')
    parser.add_argument('--show',  help='show a set of params (arg is the params key)')    
    parser.add_argument('--clear', help='clear a set of params from the registry  (arg is the service key)')
    parser.add_argument('--find',  help='find a set of params in the registry via a search string ',
                                   default="") 

    # pull out args
    args = parser.parse_args()


    if args.share:

        # pull descriptor from file
        service_params, params_name_partial = get_service_params_from_file(args.share,False)

        if not args.ver:
            print "Please specify a version label via the --ver argument"
            exit()

        params_name = "%s:%s"%(params_name_partial,args.ver)

        # validate the service description
        validation_errors = validate_service_params(service_params)

        if not validation_errors:

            # see if service has already been registered
            service_params_in_registry, params_name_in_registry = get_service_params_by_name(params_name)

            if not service_params_in_registry:
                challenge = raw_input("Please input a challenge phrase to control updates to your service params >> ")
            else:
                challenge = raw_input("Please input the challenge phrase associated with this set of service params >> ")


            print ("About to register params '%s' with challenge phrase '%s'. ")%(params_name,challenge)
            raw_input("Hit Enter to continue >> ")

            try:
                register_service_params(params_name, args.share, challenge)

                print ("Your params have been registered with yac under the key: '%s' and challenge phrase '%s'.\n" +
                       "You will prompted for the challenge phrase if you attempt to update your params.\n" + 
                       "Other users can run your params via '>> yac stack <servicename> -p %s ...'")%(params_name,challenge,params_name)

            except RegError as e:
                print ("Your params registration failed: %s"%e.msg)

        else:
            print ("Your service params failed validation checks. Please fix the following errors. %s"%validation_errors)
        

    elif args.clear:

        print "Clearing the '%s' service from registry"%(args.clear)
        challenge = raw_input("Please input the challenge phrase associated with this service >> ")        
        raw_input("Hit Enter to continue >> ")

        clear_service_params(args.clear, challenge)

        # TODO: need some success/fail feedback

    elif args.find:
        all_params = get_all_service_params_names(args.find)
        print all_params

    elif args.show:
        service_params, params_name_in_registry = get_service_params_by_name(args.show)
        if params_name_in_registry != NULL_PARAMS:
            print json.dumps(service_params,indent=2)
        else:
            print "Params requested are not available in registry"      

