#!/usr/bin/env python

import argparse, sys, json, os

from yac.lib.service import validate_service, register_service, clear_service, get_service_by_name
from yac.lib.service import get_service_from_file, publish_service_description, ServiceError

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():

    parser = argparse.ArgumentParser('Install a service in the yac registry (works a bit like an s3 bucket, but w/out the pesky security)')

    parser.add_argument('--validate', 
                        help=('validate the contents of a Servicefile '+
                              '(arg is the path to the Servicefile)'),
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--share', 
                        help=('register a service with the yac service registry so it can be provisioned by others.' +
                        ' (arg is the path to the Servicefile)'),
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--show',  help='show a service (arg is the service key)')    
    parser.add_argument('--clear', help='clear a service from the registry  (arg is the service key)')
    parser.add_argument('--find',  help=('find a service in the registry via a search string '+
                                         '(arg is search string into the registry)')) 

    # pull out args
    args = parser.parse_args()

    if args.validate:

        # pull descriptor from file
        service_descriptor, service_name, servicefile_path = get_service_from_file(args.validate)
        
        # validate the service description
        validation_errors = validate_service(service_descriptor)

        if validation_errors:
            print ("Your service description failed validation checks. Please fix the following errors. %s"%validation_errors)
        else:
            print "Service is ready to be shared!"

    elif args.share:

        # pull descriptor from file
        service_descriptor, service_name, servicefile_path = get_service_from_file(args.share)

        # validate the service description
        validation_errors = validate_service(service_descriptor, servicefile_path)

        if not validation_errors:

            # see if service has already been registered
            service_descriptor_in_registry = get_service_by_name(service_name)

            if not service_descriptor_in_registry:
                challenge = raw_input("Please input a challenge phrase to control updates to your service definition >> ")
            else:
                challenge = raw_input("Please input the challenge phrase associated with this service definition >> ")


            print ("About to register service '%s' with challenge phrase '%s'. ")%(service_name,challenge)
            raw_input("Hit Enter to continue >> ")

            try:
                register_service(service_name, args.share, challenge)

                # publish the service 
                publish_service_description(service_name, args.share)

                print ("Your service has been registered with yac under the key: '%s' and challenge phrase '%s'.\n" +
                       "You will prompted for the challenge phrase if you attempt to update your service.\n" + 
                       "Other users can run your service via '>> yac stack %s ...'")%(service_name,challenge,service_name)

            except ServiceError as e:
                print ("Your service registration failed: %s"%e.msg)

        else:
            print ("Your service description failed validation checks. Please fix the following errors. %s"%validation_errors)
        

    elif args.clear:

        print "Clearing the '%s' service from registry"%(args.clear)
        challenge = raw_input("Please input the challenge phrase associated with this service >> ")        
        raw_input("Hit Enter to continue >> ")

        clear_service(args.clear, challenge)

        # TODO: need some success/fail feedback

    elif args.find:
        print "not yet implemented"

    elif args.show:
        print "not yet implemented"        

