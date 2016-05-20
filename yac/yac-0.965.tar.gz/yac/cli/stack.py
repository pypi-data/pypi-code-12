import os, sys, json, argparse, getpass, inspect, pprint
from colorama import Fore, Style
from botocore.exceptions import ClientError
from yac.lib.file import FileError
from yac.lib.stack import create_stack, update_stack, cost_stack, get_stack_state
from yac.lib.stack import BUILDING, UPDATING, stack_exists, get_stack_templates
from yac.lib.stack import deploy_stack_files
from yac.lib.stack import UNKNOWN_STATE, UPDATABLE_STATES, NON_EXISTANT
from yac.lib.inputs import get_user_inputs, get_mapping_as_stack_params
from yac.lib.service import get_service, get_service_parmeters, get_service_alias, NULL_SERVICE, validate_service
from yac.lib.naming import set_namer, get_stack_name
from yac.lib.variables import get_variable, set_variable
from yac.lib.intrinsic import apply_custom_fxn, INSTRINSIC_ERROR_KEY
from yac.lib.params import get_service_params, NULL_PARAMS, INVALID_PARAMS
from yac.lib.vpc import get_vpc_prefs

def main():

    parser = argparse.ArgumentParser('Print a yac service to your cloud')
    
    # required args     
    parser.add_argument('servicefile',   help='location of the Servicefile (registry key or abspath)')

    # optional
    # store_true allows user to not pass a value (default to true, false, etc.)    
    parser.add_argument('-p',
                        '--params',  help='path to a file containing static service parameters (useful for keeping stack in config mgmt)') 
    parser.add_argument('-a',
                        '--alias',  help='override default service alias with this value (used for stack resource naming')    

    parser.add_argument('-d',
                        '--dryrun',  help='dry run the stack change, printing template to stdout', 
                                     action='store_true')                                                                          

    args = parser.parse_args()

    # determine service defintion, complete service name, and service alias based on the args
    service_descriptor, service_name, servicefile_path = get_service(args.servicefile) 

    # abort if service descriptor was not loaded successfully
    if service_name == NULL_SERVICE:
        print("The Servicefile input does not exist locally or in registry. Please try again.")
        exit()
    
    val_errors = validate_service(service_descriptor,servicefile_path)
    if val_errors :
        print("The Servicefile specified failed validation checks. Please fix: %s"%val_errors)
        exit()

    # determine service params based on the params arg
    service_params_input, service_params_name = get_service_params(args.params) 

    # abort if service params were not loaded successfully
    if service_params_name == NULL_PARAMS:
        print("The service params specified do not exist locally or in registry. Please try again.")
        exit()
    elif service_params_name == INVALID_PARAMS:
        print("The service params file specified failed validation checks. Please try again.")
        exit()

    # get any vpc preferences in place
    vpc_prefs = get_vpc_prefs()

    # set the resource namer to use with this service
    set_namer(service_descriptor, servicefile_path, vpc_prefs)

    # get the alias to use with this service
    service_alias = get_service_alias(service_descriptor,args.alias)

    # from the complete set of service parameters based on all stack inputs
    service_parmeters = get_service_parmeters(service_alias, service_params_input, 
                                              service_name, service_descriptor,
                                              servicefile_path, vpc_prefs)

    # get stack name
    stack_name = get_stack_name(service_parmeters)  

    # get cloud formation template for the service requested and apply yac intrinsic 
    # functions (yac-ref, etc.) using  the service_parmeters
    stack_template = get_stack_templates(service_descriptor,
                                         service_parmeters)

    # Get any reference errors recorded in the service parameters. Each represents
    # a value that should have been rendered into the stack template, but wasn't.
    reference_errors = get_variable(service_parmeters,INSTRINSIC_ERROR_KEY,"")

    # get services consumed by the service
    services_consumed = get_variable(service_parmeters,'services-consumed',[])


    # **************************** Print Time! ************************************
 
     # determine if we are building or updating this stack
    action = UPDATING if stack_exists(stack_name) else BUILDING

    if args.dryrun:

        # show stack state
        stack_state = get_stack_state(stack_name)

        # pprint stack template to a string
        stack_template_str = json.dumps(stack_template,indent=2)

        print(Fore.GREEN)

        print "%s (dry-run) the %s service aliased as '%s'"%(action,service_name,service_alias)
        print "Stack state is currently: %s."%stack_state
        print "Service stack will be named: %s"%(stack_name)

        if reference_errors:
            pp = pprint.PrettyPrinter(indent=4)
            print "Service templates include reference errors. Each should be fixed before doing an actual print."
            print pp.pprint(reference_errors)

        print_template = raw_input("Print stack template to stdout? (y/n)> ")

        if print_template and print_template=='y':
            print "Stack template:\n%s"%stack_template_str
            print "Sanity check the template above."

        print_user_inputs = raw_input("Print user inputs to stdout? (y/n)> ")

        if print_user_inputs and print_user_inputs=='y':
            # get the user inputs as a stack parameter. 
            user_inputs = get_user_inputs(service_parmeters)
            print "User inputs:\n%s"%json.dumps(user_inputs,indent=2)
            print "Sanity check the inputs above."

        print_param_mapping = raw_input("Print param mapping to stdout? (y/n)> ")

        if print_param_mapping and print_param_mapping=='y':

            stack_params = get_mapping_as_stack_params(service_parmeters)

            print "Param mapping:\n%s"%stack_params
            print "Sanity check the params above."

        estimate_cost = raw_input("Estimate the cost of the resources required by this service? (y/n)> ")

        if estimate_cost and estimate_cost=='y':

            # calc the cost of this stack, and provide url showing calculation

            # get a "costing-compatible" version of the params where all have values (to workaround a bug
            # where the costing api can't handle the UsePreviousValue flag)
            stack_params_for_costing = get_mapping_as_stack_params(service_params=service_parmeters,costing=True)

            cost_response = cost_stack(template_string = stack_template_str, 
                                       stack_params    = stack_params_for_costing)

            print "Cost of the resources for this service can be viewed here: %s"%(cost_response)

        print(Style.RESET_ALL)                      

    else:

        # make sure stack is in an buildable or updatable state before proceeding
        stack_state = get_stack_state(stack_name)

        stack_actionable = (stack_state != UNKNOWN_STATE and 
                           ((stack_state in UPDATABLE_STATES) or (stack_state == NON_EXISTANT)))

        # for reals ...
        print(Fore.GREEN)

        if not reference_errors and stack_actionable:

            # dump stack template to a string
            stack_template_str = json.dumps(stack_template)
            
            print "%s the %s service aliased as '%s'"%(action,service_name,service_alias)
            print "Service stack will be named: %s"%(stack_name)

            # give user chance to bail
            raw_input("Hit <enter> to continue..." )

            print(Style.RESET_ALL) 

            # create the service stack
            try:

                # deploy any files specified by the service
                deploy_stack_files(service_descriptor, service_parmeters, servicefile_path)

                # get parameters
                stack_params = get_mapping_as_stack_params(service_parmeters)


                if action == BUILDING:
                    response  = create_stack(stack_name = stack_name,
                                             template_string = stack_template_str,
                                             stack_params    = stack_params)

                else:
                     response = update_stack(stack_name = stack_name,
                                             template_string = stack_template_str,
                                             stack_params    = stack_params)
            
            except ClientError as e:
                print 'Service creation failed: %s'%str(e)

            except FileError as e:
                print 'Service creation failed: %s'%str(e.msg) 

        elif reference_errors:
            pp = pprint.PrettyPrinter(indent=4)
            print "Service templates include reference errors. Each must be fixed before a stack print can be performed."
            print pp.pprint(reference_errors)

        elif not stack_actionable:
            print "Stack is not currently actionable. Stack state is currently: %s."%stack_state

        # if a post function is specified, call it now
        if get_variable(service_descriptor,'post-function'):
            apply_custom_fxn(get_variable(service_descriptor,'post-function'), service_parmeters) 

        print(Style.RESET_ALL)            
