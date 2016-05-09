import os, sys, json, argparse, getpass, inspect, pprint
from colorama import Fore, Style
from botocore.exceptions import ClientError
from yac.lib.file import FileError
from yac.lib.stack import create_stack, update_stack, cost_stack
from yac.lib.stack import BUILDING, UPDATING, stack_exists, get_stack_templates
from yac.lib.stack import pretty_print_resources, deploy_stack_files
from yac.lib.service import get_service, get_service_parmeters
from yac.lib.naming import set_namer, get_stack_name
from yac.lib.variables import get_variable, set_variable
from yac.lib.intrinsic import apply_fxn, INSTRINSIC_ERROR_KEY
from yac.lib.vpc import get_vpc_prefs

def main():

    parser = argparse.ArgumentParser('Show the status of a yac stack')
    # required args
    parser.add_argument('service_alias', help='name assigned to this service in your cloud'), 

    # optional
    # store_true allows user to not pass a value (default to true, false, etc.)    
    parser.add_argument('-e',
                        '--env',  help='the environment to build stack cluster for', 
                                  choices=  ['dev','stage','prod'],
                                  default= "dev")
    parser.add_argument('--suffix',  help='to create multiple instances of the same app in the same env (e.g. confluence-intranet, confluence-tech)',
                                     default='')                                       

    args = parser.parse_args()

    # get vpc preferences in place
    vpc_prefs = get_vpc_prefs()

    # get the service parameters for use with yac-ref's in service templates
    service_parmeters = get_service_parmeters(args.service_alias, args.env, args.suffix, 
                                              "", {},
                                              "", vpc_prefs)

    # get stack name
    stack_name = get_stack_name(service_parmeters)  

    print(Fore.GREEN)

    # show stack status

    print(Style.RESET_ALL)                      
      
