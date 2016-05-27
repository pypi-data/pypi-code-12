import argparse, json, os
from yac.lib.vpc import validate_vpc_prefs, get_vpc_prefs, register_vpc_prefs
from yac.lib.vpc import set_vpc_prefs, get_vpc_prefs_from_registry, get_vpc_prefs_from_file
from yac.lib.vpc import get_all_vpc_def_keys, clear_vpc_prefs, clear_vpc_prefs_from_registry
from yac.lib.vpc import get_vpc_prefs_from_local_file
from yac.lib.paths import get_config_path
from yac.lib.variables import get_variable, set_variable

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def get_prefs_from_set(set_arg):

    validation_errors = {}

    if os.path.exists(set_arg):

        # get the preferences from file, and ensure any vpc-inputs have an 
        # absolute path
        vpc_prefs = get_vpc_prefs_from_local_file(set_arg)

        # validate the preferences
        validation_errors = validate_vpc_prefs(vpc_prefs)

    else:
        # treat the arg as the preferences key in the registry, and attempt to retrieve            
        vpc_prefs = get_vpc_prefs_from_registry(set_arg)

    return vpc_prefs, validation_errors

def main():

    parser = argparse.ArgumentParser('Manage my yac preferences')

    # optional args
    parser.add_argument('--current',  help='show the preferences currently configured',
                                      action='store_true')
    parser.add_argument('--show',  help='show a set of vpc preferences from the registry (arg is preferences name in registry)')    
    parser.add_argument('--set',   help=('set the vpc preferences to use when building stacks. ' +
                                         '(arg is prefs name for registry lookup or a path to vpc preferences file)'))
    parser.add_argument('--list',  help='list keys of all vpc preferences in the registry',
                                   action='store_true') 
    parser.add_argument('--share', help=('publish vpc preferences to the registry so they can be easily shared.'+
                                         ' arg is path to file containing the preferences'),
                                      type=lambda x: is_valid_file(parser, x))
    parser.add_argument('--clear', help='clear a vpc preference from registry (arg of "local" will clear vpc preferences currently in use locally')    
    
    args = parser.parse_args()       

    if args.current:

        vpc_prefs = get_vpc_prefs()

        print json.dumps(vpc_prefs, indent=4)

    if args.show:

        vpc_prefs = get_vpc_prefs_from_registry(args.show)

        print json.dumps(vpc_prefs,indent=4)        

    if args.share:

        # pull preferences from file
        vpc_prefs = get_vpc_prefs_from_file(args.share)

        validation_errors = validate_vpc_prefs(vpc_prefs,os.path.dirname(args.share))

        if (not validation_errors and vpc_prefs):

            vpc_prefs_name = get_variable(vpc_prefs,"prefs-name","")

            # see if these prefs have already been registered
            vpc_prefs_in_registry = get_vpc_prefs_from_registry(vpc_prefs_name)

            if not vpc_prefs_in_registry:
                challenge = raw_input("Please input a challenge phrase to control updates to your vpc preferences >> ")
            else:
                challenge = raw_input("Please input the challenge phrase associated with this vpc preference >> ")

            print ("About to register vpc definition '%s' with challenge phrase '%s'. ")%(vpc_prefs_name,challenge)
            raw_input("Hit Enter to continue >> ")

            register_vpc_prefs(vpc_prefs_name, args.share, challenge)

            print ("Your vpc preferences have been registered with yac under the key: '%s'.\n" +
                    "Other users can configure yac with these vpc prefs via '>> yac prefs --set=%s'")%(vpc_prefs_name,vpc_prefs_name)      

        elif validation_errors:
            print ("Your vpc preferences failed validation checks. Please fix the following errors.\n%s"%validation_errors)
        else:
            print ("The preferences file input doesn't contain perferences. Please try again.")

    if args.set:

        vpc_prefs, validation_errors = get_prefs_from_set(args.set)

        if (not validation_errors and vpc_prefs):

            print "Setting vpc preferences locally per '%s'."%args.set
            raw_input("Hit Enter to continue >> ")

            set_vpc_prefs(vpc_prefs)

        elif validation_errors:
            print ("Your vpc preferences failed validation checks. Please fix the following errors. %s"%validation_errors)
        else:
            print ("The preferences key input doesn't exist in the configured registry.\n" +
                   "Use >> yac prefs --list to see valid keys.")

    if args.list:

        print "The following vpc preferences are currently available in the registry"
        print get_all_vpc_def_keys() 

    if args.clear:

        if args.clear == 'local':
            print "Clearing vpc preferences currently in place"
            raw_input("Hit Enter to continue >> ")
            clear_vpc_prefs()
        else:            
            # make sure key is legit
            vpc_prefs = get_vpc_prefs_from_registry(args.clear)
            if vpc_prefs:
                challenge = raw_input("Please input the challenge phrase associated with this vpc preference >> ")
                print "Clearing the '%s' vpc preferences from registry"%args.clear
                raw_input("Hit Enter to continue >> ")
                clear_vpc_prefs_from_registry(args.clear, challenge)
            else:
                print "VPC preferences with the '%s' key do not exist in the registry"%args.clear                

