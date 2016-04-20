import os, json, jmespath
from sets import Set
from yac.lib.registry import get_registry_keys, get_remote_value, clear_entry_w_challenge
from yac.lib.registry import set_remote_string_w_challenge
from yac.lib.file import get_file_contents, register_file
from yac.lib.file_converter import convert_local_files, find_and_delete_remotes
from yac.lib.variables import get_variable, set_variable
from yac.lib.intrinsic import apply_custom_fxn
from yac.lib.vpc import get_vpc_prefs
from yac.lib.validator import validate_dictionary
from yac.lib.stack import validate_services_consumed

REQUIRED_FIELDS=["service-name.value",
                 "default-alias.value",
                 "service-description.summary",
                 "service-description.details",
                 "service-description.maintainer.name",
                 "service-description.maintainer.email"]

SUPPORTED_KEYS=[ "service-name",
                 "service-inputs",
                 "default-alias",
                 "service-description",
                 "services-consumed",
                 "resource-namer",
                 "deploy-for-boot",
                 "service-params",
                 "stack-template"]

YAC_SERVICE_SUFFIX="-service"

class ServiceError():
    def __init__(self, msg):
        self.msg = msg

def validate_service(service_descriptor):

    # get the services consumed, as specified in the server parameters
    services_consumed = get_variable(service_descriptor,'services-consumed',[])

    # check that all are valid
    val_resource_errors = validate_services_consumed(services_consumed)

    # validate the rest of the service_descriptor
    val_errors = validate_dictionary(service_descriptor, SUPPORTED_KEYS, REQUIRED_FIELDS)

    val_errors.update(val_resource_errors)
    
    return val_errors
    
def get_all_service_names():

    service_names = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with _naming suffix
    for key in registry_keys:

        if YAC_SERVICE_SUFFIX in key:
            # remove the suffix and append to list
            service_names = service_names + [key.replace(YAC_SERVICE_SUFFIX,'')]

    return service_names   

# determine service alias, service key, and service defintion based on the stack cli args
def get_service(servicefile_arg):

    service_name = ""
    service_descriptor = {}
    servicefile_path = ""

    # treat the arg as a path to a local file
    if os.path.exists(servicefile_arg):

        # service is hosted in a local file
        service_descriptor, service_name, servicefile_path = get_service_from_file(servicefile_arg)

    else:

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
        service_descriptor = get_service_by_name(service_name)

    return service_descriptor, service_name, servicefile_path

def get_service_by_name(service_name):

    service_descriptor = {}

    if service_name:

        reg_key = service_name + YAC_SERVICE_SUFFIX

        # look in remote registry
        service_contents = get_remote_value(reg_key)

        if service_contents:

            # load into dictionary
            service_descriptor = json.loads(service_contents)

    return service_descriptor

def get_service_from_file(service_descriptor_file):

    service_descriptor = {}

    # pull the service descriptor from file
    with open(service_descriptor_file) as myservice_fp:

        service_descriptor = json.load(myservice_fp)

    # pull the service name out of the descriptor
    service_name = get_variable(service_descriptor, 'service-name')

    # set the servicefile path 
    servicefile_path = os.path.dirname(service_descriptor_file)

    return service_descriptor, service_name, servicefile_path


def clear_service(service_name, challenge):

    # if service is in fact registered
    service_descriptor = get_service_by_name(service_name)
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

    print "implement me henry!"

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
        service_desc = get_service_by_name(complete_name_candidate)

        if service_desc:
            is_available = True

    return is_available

def get_complete_name(service_name):

    complete_name = ""

    if not is_service_name_complete(service_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(service_name,"latest")
        service_desc = get_service_by_name(complete_name_candidate)

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

def get_service_parmeters(service_alias, env_arg, params_file, 
                          service_name, service_descriptor,
                          servicefile_path, vpc_prefs={}):

    service_parmeters = {}

    # add params set via cli
    set_variable(service_parmeters,"service-alias",service_alias)
    set_variable(service_parmeters,"env",env_arg)
    set_variable(service_parmeters,"service-name",service_name)
    set_variable(service_parmeters,"servicefile-path",servicefile_path)

    # update with static vpc preferences 
    if "vpc-params" in vpc_prefs:
        service_parmeters.update(vpc_prefs["vpc-params"])

    # update with static service params
    if "service-params" in service_descriptor:
        service_parmeters.update(service_descriptor["service-params"])

    # update with static params specified via params file
    if params_file:
        params_from_file_str = get_file_contents(params_file)
        params_from_file = json.loads(params_from_file_str)
        service_parmeters.update(params_from_file)
        
    # add services consumed from the service descriptor to the params
    services_consumed = get_variable(service_descriptor,'services-consumed',[])
    set_variable(service_parmeters,'services-consumed',services_consumed)

    # add service description from the service summary to params
    stack_description = service_descriptor['service-description']['summary']
    set_variable(service_parmeters,'service-description',stack_description)
        
    # add service-inputs (used to drive user-prompts for params)
    if "service-inputs" in service_descriptor:        
        service_parmeters["service-inputs"] = service_descriptor["service-inputs"]

    # create dynamic vpc params via an (optional) vpc inputs scripts        
    vpc_input_script = get_variable( vpc_prefs, "vpc-inputs","")
    if vpc_input_script:
        vpc_defaults = service_parmeters.copy()    
        apply_custom_fxn(vpc_input_script, vpc_defaults)
        # save the vpc defaults back to the params
        set_variable(service_parmeters,'vpc-defaults',vpc_defaults)

    # create dynamic service params via an (optional) service inputs script
    service_input_script = get_variable(service_descriptor, "service-inputs","")
    if service_input_script:        

        apply_custom_fxn(service_input_script, service_parmeters)

    # add default values for vpc-related params if none were provided
    default_vpc_params(service_parmeters)

    return service_parmeters

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