import os, imp, urlparse

from yac.lib.paths import get_config_path, get_lib_path
from yac.lib.registry import set_remote_string_w_challenge, get_remote_value, get_registry_keys
from yac.lib.registry import set_local_value, get_local_value, delete_local_value
from yac.lib.variables import get_variable
from yac.lib.file import get_file_contents, create_customization_file, file_in_registry, get_file_reg_key

# the three functions that all services leverage.
# services can either use the defaults, or provide their
# own versions

def get_stack_name( params ):

    return get_namer_module().get_stack_name( params )

def get_resource_name( params , resource):

    return get_namer_module().get_resource_name( params , resource)

def get_namer_module():

    return imp.load_source('yac.lib.naming',get_namer())

def get_namer():

    yac_namer = get_local_value('yac_namer')

    if not yac_namer:

        # load default namer
        yac_namer = os.path.join( get_lib_path(),'naming_default.py')

    return yac_namer

def set_namer(service_descriptor, servicefile_path, vpc_prefs):

    # if a namer is specified as part of the servicefile
    if get_variable(service_descriptor, "resource-namer",""):

        service_namer_path = get_variable(service_descriptor, "resource-namer","")

        # if the file is not in the registry
        if not file_in_registry(service_namer_path):

            # assume a local path relative to the servicefile path
            service_namer_abs_path = os.path.join(servicefile_path,service_namer_path)

            if os.path.exists(service_namer_abs_path):

                # get file contents
                namer_code = get_file_contents(service_namer_abs_path)

                # associate the file with the the service name
                file_namespace = get_variable(service_descriptor,'service-name',"")
                yac_file_key = get_file_reg_key(service_namer_path,file_namespace)

                # save as a yac-local customization
                service_namer_path = create_customization_file(yac_file_key,namer_code)

        elif file_in_registry(service_namer_path):

            # save the file under yac/lib/customizations, keyed by service name
            service_namer_path = create_customization_file(service_namer_path)

    # if a namer is specified as part of the vpc preferences
    elif get_variable(vpc_prefs, "resource-namer",""):

        # Use the namer specified in the VPC preferences
        # If namer comes via the vpc preferences, it will already have been converted into a customization
        service_namer_path = get_variable(vpc_prefs, "resource-namer","") 

    else:

        # No custom namer was provided by the user.
        # Use the default namer
        service_namer_path = os.path.join( get_lib_path(),'naming_default.py')

    # save namer path to local variable
    set_local_value('yac_namer', service_namer_path)

def validate_namer_script(namer_script, prefs_path):

    val_errors = {}

    script_path = os.path.join(prefs_path,namer_script)

    if os.path.exists(script_path):

        naming_module = imp.load_source('yac.lib',script_path)

        if 'get_stack_name' not in dir(naming_module):
            val_errors.update({"stack-namer": "namer script %s lacks the get_stack_name fxn"%namer_script})

        if 'get_resource_name' not in dir(naming_module):
            val_errors.update({"resource-namer": "namer script %s lacks the get_resource_name fxn"%namer_script})

    else:
        val_errors = {"namer-script": "namer script %s doesn't exist"%namer_script}

    return val_errors    
