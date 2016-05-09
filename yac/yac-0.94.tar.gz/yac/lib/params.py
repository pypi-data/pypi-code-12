import os, json, jmespath, copy

from yac.lib.registry import get_registry_keys, get_remote_value, clear_entry_w_challenge
from yac.lib.registry import set_remote_string_w_challenge
from yac.lib.file import get_file_contents
from yac.lib.variables import get_variable, set_variable
from yac.lib.validator import validate_dictionary

NULL_PARAMS = "service params do not exist"

INVALID_PARAMS = "service params are not valid"

SERVICE_PARAMS_SUFFIX="-service-params"

REQUIRED_FIELDS = ["params-name.value",
                   "params"]

SUPPORTED_KEYS = ["params-name",
                  "params",
                  "description"]

class ServiceError():
    def __init__(self, msg):
        self.msg = msg

def validate_service_params(service_params):

    # validate the main services
    val_errors = validate_dictionary(service_params, SUPPORTED_KEYS, REQUIRED_FIELDS)
    
    return val_errors


def get_all_service_params_names(search_string=""):

    params_names = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with _naming suffix
    for key in registry_keys:

        if SERVICE_PARAMS_SUFFIX in key:
            # remove the suffix and append to list

            if search_string and search_string in key:
                params_names = params_names + [key.replace(SERVICE_PARAMS_SUFFIX,'')]

    return params_names   

# determine service alias, service key, and service defintion based on the stack cli args
# second argument allows this fxn to be called recursively in support of nested services
def get_service_params(serviceparams_arg):

    # treat the arg as a path to a local file
    service_params, params_name = get_service_params_from_file(serviceparams_arg)

    if params_name == NULL_PARAMS:

        # Service params do not exist as a local file

        # Treat serviceparams_arg as the service name. See if it is complete (i.e.
        # includes a version label)
        if is_service_params_name_complete(serviceparams_arg):

            # name is complete
            params_name = serviceparams_arg

        # Treat serviceparams_arg is a service name that lacks a version
        elif is_service_params_available_partial_name(serviceparams_arg):

            # get complete name
            params_name = get_complete_name(serviceparams_arg)

        # pull the service from the registry
        service_params, params_name = get_service_params_by_name(params_name)

    return service_params, params_name

def get_service_params_from_file(serviceparams_arg, params_only=True):

    service_params = {}
    params_name = NULL_PARAMS
    abs_path = ""

    file_contents = get_file_contents(serviceparams_arg)

    # pull the service params from file
    if file_contents:

        service_params_descriptor = json.loads(file_contents)

        # do a quick validation of the params
        if not validate_service_params(service_params_descriptor):

            # pull the service name out of the descriptor
            params_name = get_variable(service_params_descriptor, 'params-name')      

            if params_only:
                # pull the actual parameters out for return
                service_params = service_params_descriptor['params']
            else:
                # return the entire contents of the descriptor
                service_params = service_params_descriptor

        else:
            params_name = INVALID_PARAMS

    return service_params, params_name

def get_service_params_by_name(params_name):

    service_params = {}

    if params_name:

        reg_key = params_name + SERVICE_PARAMS_SUFFIX

        # look in remote registry
        service_contents = get_remote_value(reg_key)

        if service_contents:

            # load into dictionary
            service_params_descriptor = json.loads(service_contents)

            # pull the actual parameters out for return
            service_params = service_params_descriptor['params']

        else:
            # service doesn't exist
            params_name = NULL_PARAMS            

    return service_params, params_name


def clear_service_params(params_name, challenge):

    # if service is in fact registered
    service_params, params_name_returned = get_service_params_by_name(params_name)
    if service_params:

        # clear service entry registry
        reg_key = params_name + SERVICE_PARAMS_SUFFIX
        clear_entry_w_challenge(reg_key, challenge)     
    
    else:
        raise ServiceError("service params with key %s doesn't exist"%params_name)

# register service into yac registry
def register_service_params(params_name, service_path, challenge):

    if os.path.exists(service_path):

        service_contents_str = get_file_contents(service_path)

        if service_contents_str:

            reg_key = params_name + SERVICE_PARAMS_SUFFIX

            # set the service in the registry
            set_remote_string_w_challenge(reg_key, service_contents_str, challenge)

    else:
        raise ServiceError("service path %s doesn't exist"%service_path)
 

# a service name is considered complete if it includes a version tag
def is_service_params_name_complete(params_name):

    is_complete = False

    name_parts = params_name.split(':')

    if len(name_parts)==2:

        # a tag is included, so name is complete
        is_complete = True

    return is_complete  

# if only know partial service name (no label), returns true
# if the complete version of the service is in registry
def is_service_params_available_partial_name(service_partial_name):

    is_available = False

    if not is_service_params_name_complete(service_partial_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(service_partial_name,"latest")
        service_desc, params_name = get_service_params_by_name(complete_name_candidate)

        if service_desc:
            is_available = True

    return is_available

def get_complete_name(params_name):

    complete_name = ""

    if not is_service_params_name_complete(params_name):
        # see if a service with tag=latest is available in the registry
        complete_name_candidate = '%s:%s'%(params_name,"latest")
        service_desc, params_name = get_service_params_by_name(complete_name_candidate)

        if service_desc:
            complete_name = complete_name_candidate

    return complete_name



