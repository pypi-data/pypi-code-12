import boto3, jmespath
from sets import Set
from yac.lib.variables import get_variable, set_variable
from yac.lib.naming import get_stack_name
from yac.lib.stack import stack_exists, get_asg_subnet_ids, get_stack_s3_bucket, get_stack_ssh_key 
                   
def get_inputs(params):

    # get dynamic input params
    dynamic_params = get_variable(params,'service-inputs',[])

    if 'inputs' in dynamic_params:

        for param_key in dynamic_params['inputs']:

            if ('type' in dynamic_param and dynamic_param['type'] == 'scalar'):

                query_arg = dynamic_params['inputs'][param_key]['statusquo_fxn']['arg']
                                  if dynamic_params['inputs'][param_key]['statusquo_fxn']['arg']
                                  else ""

                # options
                if dynamic_params['inputs'][param_key]['constraints']['options']:
                    options = dynamic_params['inputs'][param_key]['constraints']['options']
                elif dynamic_params['inputs'][param_key]['constraints']['options_fxn']:
                    options = dynamic_params['inputs'][param_key]['constraints']['options_fxn'](params)

                set_scalar_input(params, 
                                 param_key, 
                                 dynamic_params['inputs'][param_key]['description'], 
                                 dynamic_params['inputs'][param_key]['wizard_fxn'], 
                                 dynamic_params['inputs'][param_key]['statusquo_fxn']['name'], 
                                 query_arg=query_arg):

def change_wizard(current_value, field_name, wizard_fxn):

    msg = "current %s value is %s. do you want to change? [n]/y >> "%(field_name,current_value)
    change = raw_input(msg)

    new_value = current_value

    if change and change=='y':

        # kick off the corresonding wizard function to prompt user
        # for a new value
        new_value = wizard_fxn()

    return new_value

def validated_input(msg, retry_msg, options, function):

    validation_failed = True
    
    print msg

    print "Choices include: \n%s"%pp_list(options)

    while validation_failed:

        input = raw_input("Please enter your choice >> ")

        input = input.strip("'")

        # validate the input
        validation_failed = function(input, options,retry_msg)

    return input

def validated_array_input(msg, retry_msg, options, function):

    validation_failed = True
    array_building = True

    print "enter values one at a time, cr when done ..."

    inputs = []

    while validation_failed:

        input = raw_input(msg).strip("'")

        if input:
            inputs.append(input)
        else:
            validation_failed,inputs = function(inputs, options,retry_msg)

def input_validation(input,options,retry_msg):

    # attempt to find the vpc input
    validation_failed = input not in options

    if validation_failed:
        print retry_msg

    return validation_failed

def array_validation(inputs,options,retry_msg):

    # attempt to find the vpc input
    validation_failed = len(Set(inputs) & Set(options)) != len(inputs)

    if validation_failed:
        print retry_msg
        inputs=[]

    return validation_failed, inputs    

# set the vpc to use for a given environment
def set_vpc(params):

    set_scalar_input(params,'vpc-id', 'vpc id', vpc_wizard, get_stack_vpc)

def vpc_wizard(params):

    vpc_id = validated_input("Enter id of the vpc to build in >> ", 
                             "Vpc not found, please try again", 
                             get_vpcs(),
                             input_validation)

    return vpc_id

# set the s3 bucket to use for this service
def set_s3_bucket(params):

    set_scalar_input(params,'s3-bucket', 's3 bucket', s3_bucket_wizard, get_stack_s3_bucket)       

def s3_bucket_wizard(params):

    s3_bucket = validated_input("Enter name of the s3 that should be used for backup and recovery >> ", 
                                "Bucket not found, please try again", 
                                get_s3_buckets(),
                                input_validation) 

    return s3_bucket 

# set the iam role to use for this service
def set_iam_role(params):

    set_scalar_input(params,'iam-role', 'iam role', iam_role_wizard, get_stack_iam_role )

def iam_role_wizard(params):

    iam_role = validated_input("Enter name of iam role to associate with hosts >> ", 
                               "Role invalid, please try again", 
                               get_iam_roles(),
                               input_validation) 

    return iam_role 

# set the ssh key to use for this service
def set_ssh_key(params):

    set_scalar_input(params,'ssh-key','ssh key', ssh_key_wizard, get_stack_ssh_key )

def ssh_key_wizard(params):

    key_name = validated_input("Enter name of the key pair that should be used for securing access to hosts >> ", 
                               "Key pair not found, please try again", 
                               get_key_pairs(),
                               input_validation) 

    return key_name 

# set the ssh key to use for this service
def set_ssl_cert(params):
    
    set_scalar_input(params,'ssl-cert','ssl cert', ssl_cert_wizard, get_stack_ssl_cert )

def ssl_cert_wizard(params):

    cert_name = validated_input("Enter name of the ssl cert that should be used for securing access to the ELB(s) >> ", 
                                "Cert not found, please try again", 
                                get_ssl_certs(),
                                input_validation) 

    return cert_name  

# set the snapshot id for the DB snapshot build DB from for this service
def set_db_snapshot(params):
    
    set_scalar_input(params,'snapshot-id','snapshot id', snapshot_wizard, get_stack_snapshot )    

def snapshot_wizard(params):

    app_alias = get_variable("alias")

    snapshot_id = validated_input("Enter the id of the RDS snapshot that the DB should be buit from  >> ", 
                                  "Snapshot not found, please try again", 
                                  get_snapshot_ids(app_alias),
                                  input_validation) 

    return snapshot_id 

def set_external_access(params):
    
    set_scalar_input(params,'external-access','external accesss', external_access_wizard, stack_has_external_access )

def external_access_wizard(params):

    public_access = validated_input("Does your service require access from the public internet?  >> ", 
                                    "Option not supported, please try again", 
                                     ['y','n'],
                                    input_validation) 

    public_access = public_access == 'y'

    return public_access

# set the ssh key to use for this service
def set_scalar_input(params, param_key, param_desc, wizard_fxn, stack_query_fxn, query_arg=""):

    value = ""

    # see if the param is already defined
    value = get_variable(params, param_key)

    if not value:

        # get the name of the stack
        stack_name = get_stack_name(params)

        if not stack_exists(stack_name):
            # this is a new stack...
            # prompt user for the value to use
            value = wizard_fxn(params)

        else:
            # a stack for this service already exists ...
            # determine the existing value in use
            if query_arg:
                current_value = stack_query_fxn(params, query_arg)
            else:
                current_value = stack_query_fxn(params)

            # give the user the choice of changing existing value
            value = change_wizard(current_value, param_desc, wizard_fxn )

        if value:

            set_variable(params, param_key ,value, param_desc)                

# set the ids of subnets to use
def set_subnets( params ):

    subnet_param_ids = {"dmz":     "dmz-subnet-ids", 
                        "public":  "public-subnet-ids", 
                        "private": "private-subnet-ids"}

    # set subnet ids of private subnets, since all stacks need this layer
    set_subnet_layer( params,
                      subnet_param_ids['private'], 
                      'private' )

    # if vpc has a DirectConnect route to corporate domain
    set_direct_connect(params)

    direct_connect = get_variable(params, 'direct-connect')

    if direct_connect:

        # if public internet access is needed
        set_external_access(params)

        if get_variable(params, 'external-access', False):
    
            # set the dmz subnet ids, since ASG should be placed in dmz
            set_subnet_layer( params,
                              subnet_param_ids['public'], 
                              'dmz' )

            # set public subnet ids
            set_subnet_layer( params,
                              subnet_param_ids['public'], 
                              'public' )
    else:

        # set public subnet ids
        set_subnet_layer( params,
                          subnet_param_ids['public'], 
                          'public' )

# get the subnet to use for a given vpc and a given layer
def set_subnet_layer( params, layer_param_id, layer_name ):

    # get the name of the stack
    stack_name = get_stack_name(params)

    # see if the subnets are already defined (usually via the vpc prefs)
    subnets_ids = get_variable(layer_param_id)

    if not subnets_ids:

        if not stack_exists(stack_name):

            vpc_id = get_variable("vpc-id")

            # use the wizard to prompt user for subnets
            subnets_ids = subnets_wizard(layer_name,vpc_id)

        else:

            # determine the existing subnets in use for this service
            if layer_name == "private":
                # get the current subnets based on the internal ELB
                ielb_name = get_resource_name(params,'ielb')
                subnets_ids = get_elb_subnet_ids(ielb_name)

            elif layer_name == "dmz":
                # get the subnets based on the auto-scaling group
                asg_name = get_resource_name(params,'asg')
                subnets_ids = get_asg_subnet_ids(asg_name)

        if subnets_ids:
            set_variable(params,
                         layer_param_id, 
                         subnets_ids, 
                         "%s subnet ids"%layer_name) 

def subnets_wizard(layer_name, vpc_id):

   subnet_ids = validated_array_input("Enter the id of a subnet in your %s subnet layer >> "%layer_name, 
                                      "One of more subnets not valid, please try again",
                                      get_subnets(vpc_id,get_azs()),
                                      array_validation)

   return subnet_ids

# get the ids of the vpcs available to this user
def get_vpcs():

    ec2 = boto3.client('ec2')

    # Environment tag contains VPC_MAPPING values
    vpcs = ec2.describe_vpcs()

    # get id's only
    vpc_ids = jmespath.search("Vpcs[*].VpcId", vpcs)

    return vpc_ids

# get names of available s3 buckets
def get_s3_buckets():

    s3 = boto3.client('s3')

    buckets = s3.list_buckets()

    # get names only
    bucket_names = jmespath.search("Buckets[*].Name", buckets)

    return bucket_names

# get names of available key pairs
def get_key_pairs():

    s3 = boto3.client('iam')

    public_keys = s3.list_ssh_public_keys()

    # get names only
    key_names = jmespath.search("SSHPublicKeys[*].SSHPublicKeyId", public_keys)

    return key_names

# get names of available key pairs
def get_ssl_certs():

    iam = boto3.client('iam')

    certs = iam.list_server_certificates()

    # get names only
    cert_name = jmespath.search("ServerCertificateMetadataList[*].ServerCertificateName", certs)

    return cert_name

# get names of available iam roles
def get_iam_roles():

    iam = boto3.client('iam')

    profiles = iam.list_instance_profiles()

    # get id only
    profile_ids = jmespath.search("InstanceProfiles[*].InstanceProfileId", profiles)

    return profile_ids  

# get names of available db snapshots
def get_snapshot_ids(name_search_string):

    iam = boto3.client('rds')

    filters = [{'Name':"tag:Name", 'Values' : [name_search_string]}]

    snapshots = iam.describe_db_snapshots(Filters=filters)

    # get id only
    snapshots_ids = jmespath.search("DBSnapshots[*].DBSnapshotIdentifier", snapshots)

    return snapshots_ids        

# get the zones available to this user
def get_azs():

    ec2 = boto3.client('ec2')

    # Environment tag contains VPC_MAPPING values
    azs = ec2.describe_availability_zones()

    # get id's only
    az_names = jmespath.search("AvailabilityZones[*].ZoneName", azs)

    return az_names  


# get the subnets available in a given vpc and a given set of 
# availability zones
def get_subnets(vpc_id, availabilty_zones):

    ec2 = boto3.client('ec2')
    
    subnets = ec2.describe_subnets(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        },
        {
            'Name': 'availability-zone',
            'Values': availabilty_zones
        }])

    subnet_ids = jmespath.search('Subnets[*].SubnetId',subnets)

    return subnet_ids

def pp_list(list):
    str = ""
    for item in list:
        str = str + '* %s\n'%item

    return str


