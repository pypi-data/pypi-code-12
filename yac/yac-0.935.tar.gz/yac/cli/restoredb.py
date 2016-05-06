#!/usr/bin/env python

import argparse, sys, boto3

from yac.lib.inputs import get_stack_service_inputs
from yac.lib.variables import get_variable
from yac.lib.service import get_service, NULL_SERVICE, get_service_parmeters, get_service_alias
from yac.lib.db import DB, rename_rds_instance, snapshot_exists, restore_intance_from_snapshot
from yac.lib.db import restore_security_group, delete_instance, instance_exists
from yac.lib.vpc import get_vpc_prefs
from yac.lib.naming import set_namer, get_resource_name

def prompt_for_confirmation(msg):

    sys.stdout.write('\r')                            
    sys.stdout.write( '%s%s%s'%('\033[92m',msg, '\033[0m'))
    sys.stdout.flush() 
    raw_input(" ")

def main():

    parser = argparse.ArgumentParser(description='Restore a DB from an RDS snapshot')

    # required args                                         
    parser.add_argument('instance', help='the id of the RDS instance to restore')
    parser.add_argument('snap', help='the name of the RDS snapshot to restore from')

    parser.add_argument('-d','--dryrun',  help='dry run the container start by printing rendered template to stdout', 
                                          action='store_true')

    parser.add_argument('-s','--skipto',  help='skip to this step number')

    # pull out args
    args = parser.parse_args()

    original_instance_id = args.instance

    # verify snapshot exists
    if not snapshot_exists(args.snap): 
        print "Snapshot specified does not exist. Please fix"
        exit()

    if args.dryrun:

        msg = ('\n(Dry-run) restore of the %s snapshot into the %s RDS instance.\n' +
                   'Hit <enter> to continue...')%(args.snap, original_instance_id)
        prompt_for_confirmation(msg)

    else:

        # rename the rds instance to clear the way for the restore

        # first define a new, "temp" name for the existing instance
        temp_instance_id = original_instance_id + '-temp'

        if not args.skipto or int(args.skipto) <= 1:

            if not instance_exists(original_instance_id):
                print "RDS instance specified does not exist. Please try again"
                exit()

            msg = ('About to restore the %s snapshot into the %s RDS instance \n' +
                   'Hit <enter> to continue...')%(args.snap, original_instance_id)
            prompt_for_confirmation(msg)  

            # rename the existing RDS instance
            rename_rds_instance(original_instance_id,temp_instance_id)

            msg =('(Step 1 of 3) The %s RDS instance has been renamed to %s in order to clear the way but must be rebooted before the restore can start.\n' +
                  'Hit <enter> when the %s instance shows as status=available on rds console ' +
                  ' (takes a few minutes or so) ...')%(original_instance_id,temp_instance_id,temp_instance_id)
            
            prompt_for_confirmation(msg)

        if args.skipto and int(args.skipto) <= 2:

            msg =('(Step 2 of 3) The %s snapshot can now be restored into the %s instance.\n' +
                  'Hit <enter> to proceed (takes 10 minutes or so ' +
                  ' depending on DB size) ...')%(args.snap, original_instance_id)
            prompt_for_confirmation(msg)

            restore_intance_from_snapshot(original_instance_id,temp_instance_id, args.snap)

        if args.skipto and int(args.skipto) <= 3:

            msg = ('(Step 3 of 4) The %s RDS instance has been restored from snapshot but must be rebooted before the security group can be re-applied.\n' +
                   'Hit <enter> when the instance shows as status=available on rds console (takes 15-20 minutes) ...')%(original_instance_id)
            prompt_for_confirmation(msg)

            restore_security_group(original_instance_id,original_instance_id)

        if args.skipto and int(args.skipto) <= 4:

            msg =('(Step 4 of 4) The %s RDS instance can now be deleted to complete the restore.\n' +
                  'Hit <enter> when the instance shows as status=available on rds console (takes few minutes) ...')%(temp_instance_id)
            prompt_for_confirmation(msg)

            delete_instance(temp_instance_id)

        print "Restore from snapshot is complete"