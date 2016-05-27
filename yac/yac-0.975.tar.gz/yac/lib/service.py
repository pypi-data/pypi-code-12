import os, json, jmespath, copy
from sets import Set
from yac.lib.registry import get_registry_keys, get_remote_value, clear_entry_w_challenge
from yac.lib.registry import set_remote_string_w_challenge
from yac.lib.file import get_file_contents, register_file,get_file_abs_path
from yac.lib.file_converter import convert_local_files, find_and_delete_remotes
from yac.lib.variables import get_variable, set_variable
from yac.lib.intrinsic import apply_custom_fxn
from yac.lib.vpc import get_vpc_prefs
from yac.lib.validator import validate_dictionary
from yac.lib.stack import get_stack_name, stack_exists
from yac.lib.inputs import get_inputs, get_user_inputs

NULL_SERVICE    = "servicefile does not exist"

REQUIRED_FIELDS = ["service-name.value",
                 "default-alias.value",
                 "service-description.summary",
                 "service-description.details",
                 "service-description.maintainer.name",
                 "service-description.maintainer.email"]

SUPPORTED_KEYS = [ "service-name",
                 "service-inputs",
                 "default-alias",
                 "service-description",
                 "services-consumed",
                 "resource-namer",
                 "deploy-for-boot",
                 "service-params",
                 "post-function",
                 "stack-template"]

YAC_SERVICE_SUFFIX="-service"

class ServiceError():
    def __init__(self, msg):
        self.msg = msg

def validate_service(service_descriptor, servicefile_path):

    # validate the main services
    val_errors = validate_dictionary(service_descriptor, SUPPORTED_KEYS, REQUIRED_FIELDS)
    
    # get the services consumed, as specified in the server parameters
    if 'services-consumed' in service_descriptor and 'services' in service_descriptor['services-consumed']:

        # add each sub-service specified
        for service_key in service_descriptor['services-consumed']['services']:

            sub_service_name = get_variable(service_descriptor['services-consumed']['services'],service_key)        

            # retrieve the sub-service descriptor
            sub_service_descriptor,a,b = get_service(sub_service_name, servicefile_path)

            sub_service_errors = validate_dictionary(sub_service_descriptor, SUPPORTED_KEYS, REQUIRED_FIELDS)
            val_errors.update(sub_service_errors)
    
    return val_errors


def get_all_service_names(search_str=""):

    service_names = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with _naming suffix
    for key in registry_keys:

        if key.endswith(YAC_SERVICE_SUFFIX) and (not search_str or search_str in key):
            # remove the suffix and append to list
            service_names = service_names + [key.replace(YAC_SERVICE_SUFFIX,'')]
            # service_names = service_names + [key]

    return service_names   

# determine service alias, service key, and service defintion based on the stack cli args
# second argument allows this fxn to be called recursively in support of nested services
def get_service(servicefile_arg, servicefile_path=""):

    # treat the arg as a path to a local file
    this_service_descriptor, service_name, servicefile_path = get_service_from_file(servicefile_arg, servicefile_path)

    if service_name == NULL_SERVICE:

        # Service does not exist as a local file

        # Treat servicefile_arg as the service name. See if it is complete (i.e.
        # includes a version label)
        if is_service_name_complete(servicefile_arg):

            # name is complete
            service_name = servicefile_arg

        # Treat servicefile_arg is a service name that lacks a version
        elif is_service_available_partial_name(servicefile_arg):

            # get complete name
            service_name = get_complete_name(servicefile_arg)

        # pull the service from the registry
        this_service_descriptor, service_name = get_service_by_name(service_name)

    # see if service has sub-services
    if 'services-consumed' in this_service_descriptor and 'services' in this_service_descriptor['services-consumed']:

        # add each sub-service specified
        for service_key in this_service_descriptor['services-consumed']['services']:

            sub_service_name = get_variable(this_service_descriptor['services-consumed']['services'],service_key)

            sub_service_comment = this_service_descriptor['services-consumed']['services'][service_key]['comment']

            print "adding '%s' services from %s ..."%(sub_service_comment,sub_service_name)

            # do a recursive call to retrieve the sub-service descriptor
            # sub's can't change service_name or servicefile_path, so return them to placeholders (a,b) ...
            sub_service_descriptor,a,b = get_service(sub_service_name, servicefile_path)

            update_service_descriptor(this_service_descriptor, sub_service_descriptor)

    return this_service_descriptor, service_name, servicefile_path

def get_service_from_file(servicefile_arg, servicefile_path=""):

    service_descriptor = {}
    service_name = NULL_SERVICE
    abs_path = ""

    file_contents = get_file_contents(servicefile_arg, servicefile_path)

    # pull the service descriptor from file
    if file_contents:

        service_descriptor = json.loads(file_contents)

        # pull the service name out of the descriptor
        service_name = get_variable(service_descriptor, 'service-name')

        # the servicefile_arg could be relative to servicefile_path (if 
        # this is a local sub-service) or absolute
        # determine the absolute path for either condition
        abs_path = get_file_abs_path(servicefile_arg, servicefile_path)       

    # initialize mergeable fields to defaut values
    init_mergeable_fields(service_descriptor)

    return service_descriptor, service_name, abs_path

def get_service_by_name(service_name):

    service_descriptor = {}

    if service_name:

        reg_key = service_name + YAC_SERVICE_SUFFIX

        # look in remote registry
        service_contents = get_remote_value(reg_key)

        if service_contents:

            # load into dictionary
            service_descriptor = json.loads(service_contents)

        else:
            # service doesn't exist
            service_name = NULL_SERVICE

    # initialize mergeable fields to defaut values
    init_mergeable_fields(service_descriptor)            

    return service_descriptor, service_name

def update_service_descriptor(service_descriptor, sub_service_descriptor):

    # merge inputs
    service_descriptor["service-inputs"]["inputs"].update(sub_service_descriptor["service-inputs"]["inputs"])
    service_descriptor["service-inputs"]["conditional-inputs"].update(sub_service_descriptor["service-inputs"]["conditional-inputs"])

    # merge params
    service_descriptor["service-params"].update(sub_service_descriptor["service-params"])

    # merge stack Parameters
    service_descriptor["stack-template"]["Parameters"].update(sub_service_descriptor["stack-template"]["Parameters"])

    # merge stack Resources
    service_descriptor["stack-template"]["Resources"].update(sub_service_descriptor["stack-template"]["Resources"])

    # merge stack Conditions
    service_descriptor["stack-template"]["Conditions"].update(sub_service_descriptor["stack-template"]["Conditions"])


# if "mergeable" fields are empty, initi them to null in order to make descriptor mergers easier
def init_mergeable_fields(service_descriptor):

    if "service-params" not in service_descriptor:
        service_descriptor["service-params"] = {}

    if "service-inputs" not in service_descriptor:
        service_descriptor["service-inputs"] = {
                                                "inputs": {},
                                                "conditional-inputs": {}
                                                }

    # stack Parameters
    if "stack-template" not in service_descriptor:
        service_descriptor["stack-template"] = {}

    if "Parameters" not in service_descriptor["stack-template"]:
        service_descriptor["stack-template"]["Parameters"] = {}

    if "Resources" not in service_descriptor["stack-template"]:

        service_descriptor["stack-template"]["Resources"] = {}

    if "Conditions" not in service_descriptor["stack-template"]:
        service_descriptor["stack-template"]["Conditions"] = {}


def clear_service(service_name, challenge):

    # if service is in fact registered
    service_descriptor, service_name_returned = get_service_by_name(service_name)
    if service_descriptor:

        # clear service entry registry
        reg_key = service_name + YAC_SERVICE_SUFFIX
        clear_entry_w_challenge(reg_key, challenge)

        # clear any files referenced 
        find_and_delete_remotes(service_descriptor, challenge)      
    
    else:
        raise ServiceError("service with key %s doesn't exist"%service_name)

# register service into yac registry
def register_service(service_name, service_path, challenge):

    if os.path.exists(service_path):

        service_contents_str = get_file_contents(service_path)

        if service_contents_str:

            reg_key = service_name + YAC_SERVICE_SUFFIX

            # get the base path of the service file
            servicefile_path = os.path.dirname(service_path)

            updated_service_contents_str = convert_local_files(service_name,
                                                  service_contents_str,
                                                  servicefile_path,
                                                  challenge)

            # set the service in the registry
            set_remote_string_w_challenge(reg_key, updated_service_contents_str, challenge)

    else:
        raise ServiceError("service path %s doesn't exist"%service_path)

# service_name formatted as:
#  <organization>/<service>:<version>
# service_path is path to the file container the service descriptor
def publish_service_description(service_name, service_path):

    print "stub for service publication to human-readable docs - not yet implemented"

def is_service_alias(service_alias, vpc_prefs):

    is_alias = False

    # see if alias is a name in our vpc_prefs alias dict
    if "aliases" in vpc_prefs and service_alias in vpc_prefs['aliases']:
        is_alias = True

    return is_alias

def get_alias_from_name(complete_service_name):

    alias = ""

    if complete_service_name:

        name_parts = complete_service_name.split(':')

        # see if first part can be further split
        name_prefix_parts = name_parts[0].split('/')

        # treat the alias as the last of the prefix parts
        alias = name_prefix_parts[-1]

    return alias

def get_service_name(service_alias, vpc_prefs):

    server_name = ""
    # see if alias is a name in our vpc_prefs alias dict
    if "aliases" in vpc_prefs and service_alias in vpc_prefs['aliases']:
        server_name = vpc_prefs['aliases'][service_alias]

    return server_name 

# a service name is considered complete if it includes a version tag
def is_service_name_complete(service_name):

    is_complete = False

    name_parts = service_name.split(':')

    if len(name_parts)==2:

        # a tag is included, so name is complete
        is_complete = True

    return is_complete  

# if only know partial service name (no label), returns true
# if the complete version of the service is in registry
def is_service_available_partial_name(service_partial_name):

    is_available = False

    if not is_service_name_complete(service_partial_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(service_partial_name,"latest")
        service_desc, service_name = get_service_by_name(complete_name_candidate)

        if service_desc:
            is_available = True

    return is_available

def get_complete_name(service_name):

    complete_name = ""

    if not is_service_name_complete(service_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(service_name,"latest")
        service_desc, service_name = get_service_by_name(complete_name_candidate)

        if service_desc:
            complete_name = complete_name_candidate

    return complete_name

def get_service_alias(service_descriptor,service_alias_arg):

    # if service alias was provided in cli, use that as the alias.
    # o.w., use the default alias specified in the servicefile
    if service_alias_arg:
        service_alias = service_alias_arg
    else:
        service_alias = get_variable(service_descriptor,"default-alias")

    return service_alias

def get_service_parmeters(service_alias, service_params_via_cli, 
                          service_name, service_descriptor,
                          servicefile_path, vpc_prefs={}):

    service_parmeters = {}

    # update with static vpc preferences. do this first (so params specified
    # in servicefile and/or params file will override params specified 
    # via vpc preferences) 
    if "vpc-params" in vpc_prefs:
        service_parmeters.update(vpc_prefs["vpc-params"])

    # add params set via cli
    set_variable(service_parmeters,"service-alias",service_alias)
    set_variable(service_parmeters,"service-name",service_name)
    set_variable(service_parmeters,"servicefile-path",servicefile_path)

    # update with static service params specified via the servicefile
    if "service-params" in service_descriptor:
        service_parmeters.update(service_descriptor["service-params"])

    # update with static params specified via cli params file
    if service_params_via_cli:
        service_parmeters.update(service_params_via_cli)
        
    # add services consumed from the service descriptor to the params
    services_consumed = get_variable(service_descriptor,'services-consumed',[])
    set_variable(service_parmeters,'services-consumed',services_consumed)

    # add service description from the service summary to params
    stack_description = service_descriptor['service-description']['summary']
    set_variable(service_parmeters,'service-description',stack_description)
        
    # add service-inputs (used to drive user-prompts for params)
    if "service-inputs" in service_descriptor:        
        service_parmeters["service-inputs"] = service_descriptor["service-inputs"]

    # create dynamic vpc params via an (optional) set of service-inputs
    if "service-inputs" in vpc_prefs:
        
        # initialize a separate set of service params for use in vpc inputs
        # script. This will allow us to differentiate vpc-preference-generated 
        # inputs from other inputs.
        vpc_defaults = service_parmeters.copy()
        vpc_defaults['service-inputs'] = vpc_prefs["service-inputs"]

        vpc_inputs_script = get_variable( vpc_prefs, "service-inputs","")

        if vpc_inputs_script:
            # gather inputs via custom script
            apply_custom_fxn(vpc_inputs_script, vpc_defaults)
        else:
            # gather inputs via 'stock' fxn
            get_inputs(vpc_defaults)

        # save the vpc defaults back to the params
        set_variable(service_parmeters,'vpc-defaults',vpc_defaults)

        # Inputs entered by user should be treated the same as input provided by
        # a params file, so save them into the stack params for downstream use.
        service_parmeters.update(get_variable(vpc_defaults,'user-inputs'))

    # create dynamic service params via an (optional) service inputs script
    if "service-inputs" in service_descriptor:

        service_input_script = get_variable(service_descriptor, "service-inputs","")

        if service_input_script:
            # gather inputs via custom script
            apply_custom_fxn(service_input_script, service_parmeters)
        else:
            # gather inputs via 'stock' fxn
            get_inputs(service_parmeters)

    # merge user inputs collected from servicefile and render into string that can be used 
    # in a Stack parameters value
    # Strip out the comments fields to preserve space (this string will be saved to a string in stack parameters, and
    # and stack params are limitted in length)
    user_inputs = get_user_inputs(service_parmeters)

    inputs_copy = copy.deepcopy(user_inputs)

    set_variable(service_parmeters,
                'user-inputs-str', 
                json.dumps(prune_inputs(inputs_copy)), 
                "Inputs provided by users, as a string")

    # add default values for vpc-related params if none were provided
    default_vpc_params(service_parmeters)

    # add stack name and state 
    stack_name = get_stack_name(service_parmeters)
    set_variable(service_parmeters,'stack-name',stack_name, "Name of the service stack")
    set_variable(service_parmeters,'stack-exists',stack_exists(stack_name), "Stack exists")

    return service_parmeters

def prune_inputs(user_inputs):

    # remove comment field
    for key in user_inputs:
        if 'comment' in user_inputs[key]:
            user_inputs[key].pop('comment')

    return user_inputs

# set default values for vpc-related params (proxy, corporate cidr, etc.)
def default_vpc_params(service_parmeters):

    if not get_variable(service_parmeters,'proxy-port',""):
        set_variable(service_parmeters,'proxy-port',"")

    if not get_variable(service_parmeters,'proxy-cidr',""):
        set_variable(service_parmeters,'proxy-cidr',"")

    if not get_variable(service_parmeters,'corporate-cidr',""):
        set_variable(service_parmeters,'corporate-cidr',"")

    if not get_variable(service_parmeters,'dns-cidr',""):
        set_variable(service_parmeters,'dns-cidr',"0.0.0.0/0")        

    if not get_variable(service_parmeters,'ntp-servers',""):
        set_variable(service_parmeters,'ntp-servers',"0.pool.ntp.org;1.pool.ntp.org;2.pool.ntp.org;3.pool.ntp.org")     