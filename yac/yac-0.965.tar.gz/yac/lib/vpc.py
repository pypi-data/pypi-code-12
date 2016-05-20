import os, json, jmespath, boto3
from botocore.exceptions import ClientError
from yac.lib.paths import get_config_path
from yac.lib.registry import set_remote_string_w_challenge, get_remote_value, get_registry_keys
from yac.lib.registry import set_local_value, get_local_value, clear_entry_w_challenge
from yac.lib.validator import validate_dictionary
from yac.lib.file_converter import convert_local_files, find_and_delete_remotes
from yac.lib.variables import get_variable, set_variable
from yac.lib.file import get_file_contents, create_customization_file, get_file_reg_key
from yac.lib.naming import validate_namer_script
from yac.lib.inputs import validate_inputs_script

YAC_VPC_SUFFIX="-vpc"

REQUIRED_FIELDS=["prefs-name.value",
                 "vpc-params"]

SUPPORTED_KEYS=[ "prefs-repo",
                 "prefs-name",
                 "vpc-inputs",
                 "vpc-params",
                 "resource-namer",
                 "service-inputs",
                 "service-templates"]

def validate_vpc_prefs(vpc_prefs, prefs_path = ""):

    prefs_errors = validate_dictionary(vpc_prefs, SUPPORTED_KEYS, REQUIRED_FIELDS)

    # if a namer is specified as part of the vpc preferences
    namer_script = get_variable(vpc_prefs, "resource-namer","")
    
    if namer_script:
        namer_errors = validate_namer_script(namer_script, prefs_path)

        prefs_errors.update(namer_errors)

    # if an inputs script is specified as part of the vpc preferences
    if "service-inputs" in vpc_prefs:
        
        inputs_script = get_variable( vpc_prefs, "service-inputs","")
        
        if inputs_script:            
            inputs_errors = validate_inputs_script(inputs_script, prefs_path)

            prefs_errors.update(inputs_errors)        

    return prefs_errors

def get_vpc_prefs():

    vpc_preferences = get_local_value('vpc_preferences')

    return vpc_preferences

def set_vpc_prefs(vpc_prefs):

    if vpc_prefs:

        # save vpc preferences to local db
        set_local_value('vpc_preferences',vpc_prefs)

def clear_vpc_prefs():

    set_local_value('vpc_preferences',{})

# register namer into yac registry
def register_vpc_prefs(vpc_prefs_key, vpc_prefs_file, challenge):

    with open(vpc_prefs_file) as vpc_prefs_file_fp:

        vpc_preferences_str = vpc_prefs_file_fp.read()

        vpc_prefs_file_path = os.path.dirname(vpc_prefs_file)

        updated_vpc_preferences_str = convert_local_files(vpc_prefs_key,
                                          vpc_preferences_str,
                                          vpc_prefs_file_path,
                                          challenge)

        # add the suffix to distinguish this key as a vpc preferences key
        vpc_prefs_registry_key = vpc_prefs_key + YAC_VPC_SUFFIX

        # set the vpc defs in the registry
        set_remote_string_w_challenge(vpc_prefs_registry_key, updated_vpc_preferences_str, challenge)

def clear_vpc_prefs_from_registry(vpc_prefs_name, challenge):

    # if vpc preferences are in fact registered
    vpc_prefs = get_vpc_prefs_from_registry(vpc_prefs_name)
    
    if vpc_prefs:

        # add the suffix to distinguish this key as a vpc preferences key
        vpc_prefs_registry_key = vpc_prefs_name + YAC_VPC_SUFFIX

        # clear the vpc defs from the registry
        clear_entry_w_challenge(vpc_prefs_registry_key, challenge)

        # clear any files referenced 
        find_and_delete_remotes(vpc_prefs, challenge) 

def get_vpc_prefs_from_file(prefs_file_path):

    vpc_prefs = {}
    vpc_prefs_name = ""

    with open(prefs_file_path) as vpc_prefs_file_fp:

        vpc_prefs = json.load(vpc_prefs_file_fp)

    return vpc_prefs

def get_vpc_prefs_from_registry(vpc_def_registry_key):

    vpc_prefs = {}

    if vpc_def_registry_key:

        # get vpc defs from registry
        vpc_prefs_str = get_remote_value('%s-vpc'%vpc_def_registry_key)

        if vpc_prefs_str:

            # convert back to dictionary
            vpc_prefs = json.loads(vpc_prefs_str)

            # see if an inputs script is specified
            vpc_inputs_yac_path = get_variable(vpc_prefs,'service-inputs',"")
            
            print 'inputs path: %s'%vpc_inputs_yac_path
            
            if vpc_inputs_yac_path:

                # save the file under yac/lib/customizations
                inputs_file_local_path = create_customization_file(vpc_inputs_yac_path)

                # save the  new path back to the preferences
                vpc_prefs['service-inputs']['value'] = inputs_file_local_path

            # If the vpc prefs references a namer script, then we need to save it
            # as a yac customization so it can be executed against any Scriptfile.

            # see if a namer script is specified
            vpc_namer_yac_path = get_variable(vpc_prefs,'resource-namer',"")

            if vpc_namer_yac_path:

                # save the file as a yac-local customization
                namer_file_local_path = create_customization_file(vpc_namer_yac_path)

                # change file reference so that instrincs recognizes it as part of the yac sources
                set_variable(vpc_prefs,'resource-namer', namer_file_local_path)

    return vpc_prefs

def get_all_vpc_def_keys():

    vpc_prefs = []

    # get all registry keys
    registry_keys = get_registry_keys()

    # find all keys with -vpc suffix
    for key in registry_keys:

        if '-vpc' in key:
            # remove the naming part
            vpc_prefs = vpc_prefs + [key.replace('-vpc','')]

    return vpc_prefs  

# get vpc preferences from a local file
def get_vpc_prefs_from_local_file(vpc_prefs_file):

    vpc_prefs = get_vpc_prefs_from_file(vpc_prefs_file)

    vpc_prefs_name = get_variable(vpc_prefs,'prefs-name',"")

    prefs_path = os.path.dirname(vpc_prefs_file)

    # If the vpc prefs references a vpc-inputs script, then we need to save it
    # as a yac customization so it can be executed against any Scriptfile.

    # see if an inputs script is specified
    vpc_inputs_script_path = get_variable(vpc_prefs,'service-inputs',"")
    
    if vpc_inputs_script_path:

        # use the preferences name for the inputs file namespace
        yac_file_key = get_file_reg_key(vpc_inputs_script_path,vpc_prefs_name)

        prefs_file_contents = get_file_contents(os.path.join(prefs_path,vpc_inputs_script_path))

        # save the file under yac/lib/customizations
        inputs_file_yac_path = create_customization_file(yac_file_key,prefs_file_contents)

        # save the  new path back to the preferences
        vpc_prefs['service-inputs']['value'] = inputs_file_yac_path

    # If the vpc prefs references a namer script, then we need to save it
    # as a yac customization so it can be executed against any Scriptfile.

    # see if a namer script is specified
    vpc_namer = get_variable(vpc_prefs,'resource-namer',"")

    if vpc_namer:

        # use the preferences name for the namer file namespace
        yac_file_key = get_file_reg_key(vpc_namer,vpc_prefs_name)

        namer_contents = get_file_contents(os.path.join(prefs_path,vpc_namer))

        # save the file as a yac-local customization
        namer_file_yac_path = create_customization_file(yac_file_key,namer_contents)

        # change file reference so that instrincs recognizes it as part of the yac sources
        set_variable(vpc_prefs,'resource-namer', namer_file_yac_path)


    return vpc_prefs 

# get the subnets to use for a given vpc and a given set of 
# availability zones
def set_dmz_subnets( vpc_id ):

    # get the env
    env  = get_variable(params,'env')

    # get the name of the stack
    stack_name = get_stack_name(params)

    subnet_ids=[]

    if not stack_exists(stack_name):

        # see if the subnets are already defined (usually via the vpc prefs)
        dmz_subnets_prefs = get_variable("dmz-subnet-ids")

        if not dmz_subnets_prefs:

            # use the wizard to prompt user for subnets
            subnet_ids = subnets_wizard()

        else:
            subnet_ids = vpcs_per_prefs

    else:

        # determine the existing private subnets in use for this service
        subnet_ids = get_stack_private_subnets(params)

    return vpc

# get the availability zones to use for a given environment
def _get_availability_zones(params):

    azs = {}

    # get the env
    env  = get_variable(params,'env')

    # get the name of the stack
    stack_name = get_stack_name(params)

    if not stack_exists(stack_name):

        # get availability zones from params
        availabilty_zones = get_variable(params,"availability-zones",[])

        # see if the vpc is already defined (usually via the vpc prefs)
        azs_per_prefs = get_variable(params,'vpc-id')

        if not vpcs_per_prefs:

            # use the default vpc for this env, per vpc_mapping
            azs = get_vpc_wizard()

        else:
            azs = vpcs_per_prefs

    else:

        # determine the existing VPC in use for this service
        azs = get_stack_vpc(params)

    return azs    

