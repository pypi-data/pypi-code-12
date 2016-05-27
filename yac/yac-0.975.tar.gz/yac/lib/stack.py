#!/usr/bin/env python
import os, json, urlparse, boto3, subprocess, shutil, jmespath
from botocore.exceptions import ClientError
from sets import Set
from yac.lib.file import FileError, file_in_registry, get_file_contents, localize_file
from yac.lib.template import apply_templates_in_file, apply_templates_in_dir
from yac.lib.paths import get_config_path
from yac.lib.intrinsic import apply_fxn
from yac.lib.variables import get_variable, set_variable
from yac.lib.naming import get_stack_name

UPDATING = "Updating"
BUILDING = "Building"

STACK_STATES = ['CREATE_IN_PROGRESS','CREATE_FAILED','CREATE_COMPLETE','ROLLBACK_IN_PROGRESS',
                'ROLLBACK_FAILED','ROLLBACK_COMPLETE','DELETE_IN_PROGRESS','DELETE_FAILED',
                'DELETE_COMPLETE','UPDATE_IN_PROGRESS','UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_COMPLETE','UPDATE_ROLLBACK_IN_PROGRESS','UPDATE_ROLLBACK_FAILED',
                'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_ROLLBACK_COMPLETE']

CREATE_IN_PROGRESS_STATE = 'CREATE_IN_PROGRESS'

NEWLY_CREATED_STATE = 'CREATE_COMPLETE'

UPDATE_COMPLETE_STATE = 'UPDATE_COMPLETE'

UPDATE_IN_PROGRESS_STATE = 'UPDATE_IN_PROGRESS'

UPDATABLE_STATES = ['CREATE_COMPLETE','UPDATE_COMPLETE','UPDATE_ROLLBACK_COMPLETE']

UNKNOWN_STATE = "unknown"

NON_EXISTANT = "non-existant"

# determine cost of a new stack
def cost_stack( template_string="", stack_params = None ):

    cost_response = ""

    client = boto3.client('cloudformation')

    try:

        response = client.estimate_template_cost(TemplateBody=template_string,
                                                 Parameters = stack_params)

        cost_response = str(response['Url'])

    except ClientError as e:
        
        cost_response = 'Stack costing failed: %s'%str(e)

    return cost_response

def create_stack( stack_name , 
                  template_string="", 
                  stack_params = [],
                  stack_tags = []):

    client = boto3.client('cloudformation')

    response = client.create_stack(StackName=stack_name,
                                 TemplateBody=template_string,
                                 Parameters = stack_params,
                                 Tags=stack_tags,
                                 Capabilities=['CAPABILITY_IAM'])

    print 'Stack creation in progress - use AWS console to watch construction and/or see errors'

    return response


def update_stack( stack_name , 
                  template_string="", 
                  stack_params = [],
                  stack_tags = []):

    client = boto3.client('cloudformation')

    response = client.update_stack(StackName=stack_name,
                                   TemplateBody=template_string,
                                   Parameters = stack_params,
                                   Capabilities=['CAPABILITY_IAM'])

    print 'Stack update in progress - use AWS console to watch updates and/or see errors'

    return response       

def get_stack_state( stack_name ):

    client = boto3.client('cloudformation')

    if stack_exists( stack_name ):

        response = client.describe_stacks(StackName=stack_name)

        states = jmespath.search("Stacks[*].StackStatus",response)

        if len(states) == 1:
            state = states[0]
        else:
            state = UNKNOWN

    else:
        state = NON_EXISTANT

    return state 

def get_stack_templates(service_descriptor, service_parmeters):

    service_template = {}

    # get the template from the service_descriptor
    if 'stack-template' in service_descriptor:

        # get the template from the descriptor
        service_template_with_refs = service_descriptor['stack-template']

        # get any resources that are to be excluded based on user input
        resource_exclusions = get_variable(service_parmeters,'resource-exclusions',[])

        for resource in resource_exclusions:
            if resource in service_template_with_refs['Resources']:
                print "removing the %s resource per requested exclusion ..."%resource
                service_template_with_refs['Resources'].pop(resource) 

        # render intrinsics
        service_template = apply_fxn(service_template_with_refs, service_parmeters)

    return service_template

def get_stack_templates_old(service_descriptor, vpc_prefs, service_parmeters):

    # get the services this service consumes
    services_consumed = get_variable(service_descriptor,'services-consumed',[])

    # get the template files to use based on services specified
    template_files = _get_stock_template_files(services_consumed, vpc_prefs) 

    # combine all resources into a single stack dictionary
    stack_template = {}

    for key in template_files.keys():

        print "merging in the cf template in %s for the %s service ..."%(template_files[key],key)
        
        # pull template from file into a dictionary while also rendering any service 
        # parmeters into the dictionary
        this_resource_template = get_stackdef_from_file(template_files[key],
                                                        service_parmeters)

        # merge this resource into the stack definition
        stack_template = update_template(stack_template,this_resource_template)


    # next add any resources or resource changes specified in the service_descriptor
    if 'stack-template' in service_descriptor:

        # first render intrinsics
        service_template = apply_fxn(service_descriptor['stack-template'], service_parmeters)

        # merge these resources into the stack definition
        stack_template = update_template(stack_template,service_template)


    return stack_template

def _get_stock_template_files(services_consumed, vpc_prefs):

    stock_templates = {}
    vpc_prefs_template_map = {}

    # get template map provided in the vpc preferences
    if 'service-templates' in vpc_prefs:
        vpc_prefs_template_map = vpc_prefs['service-templates']

    # default templates supported
    template_map = {
        "asg":   "yac-asg-stack.json",
        "rds":   "yac-db-stack.json",
        "e-elb": "yac-eelb-stack.json",
        "i-elb": "yac-ielb-stack.json",
        "efs":   "yac-efs-stack.json"
    }

    # override the default template map per vpc preferences
    template_map.update(vpc_prefs_template_map)

    config_path = os.path.join(get_config_path(),'stack')

    for resource_key in services_consumed:

        if not file_in_registry(template_map[resource_key]):
            # use the local file
            stock_templates[resource_key] = os.path.join(config_path,template_map[resource_key])
        else:
            # use the file in the registry
            stock_templates[resource_key] = template_map[resource_key]

    return stock_templates

# Inputs are two cloud formation templates.
# Merge the to_add_template into the base_template
def update_template(base_template, to_add_template):

    if 'Description' in to_add_template:
        # add a stack-specific description
        base_template['Description'] = to_add_template['Description']

    if 'Conditions' in to_add_template:

        # first make sure Parameters is present in base template
        if 'Conditions' not in base_template:
            base_template['Conditions'] = {}

        for key in to_add_template['Conditions'].keys():

            base_template['Conditions'][key] = to_add_template['Conditions'][key]

    if 'Parameters' in to_add_template:

        # first make sure Parameters is present in base template
        if 'Parameters' not in base_template:
            base_template['Parameters'] = {}

        for key in to_add_template['Parameters'].keys():

            base_template['Parameters'][key] = to_add_template['Parameters'][key]

    if 'Mappings' in to_add_template:

        # first make sure Resources is present in base template
        if 'Mappings' not in base_template:
            base_template['Mappings'] = {}

        for key in to_add_template['Mappings'].keys():

            base_template['Mappings'][key] = to_add_template['Mappings'][key]

    if 'Resources' in to_add_template:

        # first make sure Resources is present in base template
        if 'Resources' not in base_template:
            base_template['Resources'] = {}

        for key in to_add_template['Resources'].keys():

            base_template['Resources'][key] = to_add_template['Resources'][key]            

    if 'ResourceTweaks' in to_add_template:

        # 'tweak' resources in the standard stack
        for sg_key in to_add_template['ResourceTweaks'].keys():

            # assume Security group changes are additions
            if to_add_template['ResourceTweaks'][sg_key]['Type'] == "AWS::EC2::SecurityGroup":

                for second_tier_key in to_add_template['ResourceTweaks'][sg_key]['Properties'].keys():

                    if second_tier_key == "SecurityGroupEgress":

                        # add special egress rule
                        base_template = _append_sg_rule(base_template, 
                                                        to_add_template,
                                                        sg_key,
                                                        "SecurityGroupEgress")
                
                    elif second_tier_key == "SecurityGroupIngress":

                        # add special ingress rule
                        base_template = _append_sg_rule(base_template, 
                                                        to_add_template,
                                                        sg_key,
                                                        "SecurityGroupIngress")

            # add property changes
            else:

                for second_tier_key in to_add_template['ResourceTweaks'][sg_key]['Properties'].keys():

                    base_template['Resources'][sg_key]['Properties'][second_tier_key] = to_add_template['ResourceTweaks'][sg_key]['Properties'][second_tier_key]                     

    return base_template

def _append_sg_rule(base_template, to_add_template, sg_key, rule_type):

    for egress_rule in to_add_template['ResourceTweaks'][sg_key]['Properties'][rule_type]:

        # add and rules to base template
        base_template['Resources'][sg_key]['Properties'][rule_type].append(egress_rule)

    return base_template    

# returns stack template as a dictionary.
# render any yac intrinsics present in the dictionary
def get_stackdef_from_file(template_path, service_parmeters={}):

    stack_definitions = {}

    stack_defs_str = get_file_contents(template_path)

    if stack_defs_str:
        
        stack_definitions = json.loads(stack_defs_str)

        # render yac intrinsics in the stack definition
        stack_definitions = apply_fxn(stack_definitions, service_parmeters) 

    return stack_definitions

def stack_exists(stack_name):

    client = boto3.client('cloudformation')

    try:
        response = client.describe_stacks(StackName=stack_name)
        stack_count = len(response['Stacks'])
        return stack_count>0
    except:
        return False

def deploy_stack_files(service_descriptor, service_parmeters, servicefile_path): 

    # deploy any individual files that the service needs before booting
    # (default to empty array in case variable is not defined)
    files_for_boot = get_variable(service_descriptor, 'deploy-for-boot', [], 'files')

    # render service parmeters in the files then deploy 'em
    _load_files(files_for_boot, service_parmeters, servicefile_path)

    # deploy any directories that the service needs before booting
    dirs_for_boot = get_variable(service_descriptor, 'deploy-for-boot', [], 'directories')

    # render service parmeters in the files contained in the directories then deploy
    # the directory structure to destination
    _load_dirs(dirs_for_boot, service_parmeters)


# Render service parmeters into file body, then load files to destination
# Only s3 destinations are currently supported.
def _load_files(files, service_parmeters, servicefile_path):

    # assume the file path is relative to the location
    # of the service descriptor file (just like Dockerfile!)
    servicefile_path = get_variable(service_parmeters,"servicefile-path")

    for this_ifile in files:

        # render intrinsics in the file dictionary
        this_file = apply_fxn(this_ifile, service_parmeters)      

        # if necessary, localize file
        localized_file = localize_file(this_file['src'], servicefile_path)

        # plan to render the file into a 'tmp' directory under the servicefile dir
        rendered_file_path = os.path.join(servicefile_path,'tmp')

        if os.path.exists(localized_file):

            # replace any service parmeters variables in the file body and return the 
            # name+path of the "rendered" file
            rendered_file = apply_templates_in_file(localized_file, service_parmeters, rendered_file_path)
  
            # if destination is s3 bucket
            if (is_s3_destination(this_file['dest']) and rendered_file):

                # copy rendered file to s3 destination 
                cp_file_to_s3( rendered_file, this_file['dest'])

            # if destination is another local file (mostly used for testing)
            else:

                # make sure destination directory exists
                if not os.path.exists(os.path.dirname(this_file['dest'])):
                    os.makedirs(os.path.dirname(this_file['dest']))

                # copy rendered file to the destination
                shutil.copy(rendered_file,this_file['dest']) 

        else:

            raise FileError( "%s file deploy was not performed. Source file is missing"%localized_file )


# Render service parmeters into file body, then load files to destination
# Only s3 destinations are currently supported.
def _load_files_old(files, service_parmeters):

    # assume the file path is relative to the location
    # of the service descriptor file (just like Dockerfile!)
    servicefile_path = get_variable(service_parmeters,"servicefile-path")

    for this_ifile in files:

        # render intrinsics in the file dictionary
        this_file = apply_fxn(this_ifile, service_parmeters)      

        source_path = os.path.join(servicefile_path,this_file['src'])

        # render the file into a 'tmp' directory under the servicefile dir
        rendered_file_path = os.path.join(servicefile_path,'tmp')

        if os.path.exists(source_path):

            # replace any service parmeters variables in the file body and return the 
            # name+path of the "rendered" file
            rendered_file = apply_templates_in_file(source_path, service_parmeters, rendered_file_path)
  
            # if destination is s3 bucket
            if (is_s3_destination(this_file['dest']) and rendered_file):

                # copy rendered file to s3 destination 
                cp_file_to_s3( rendered_file, this_file['dest'])

            # if destination is another local file (mostly used for testing)
            else:

                # make sure destination directory exists
                if not os.path.exists(os.path.dirname(this_file['dest'])):
                    os.makedirs(os.path.dirname(this_file['dest']))

                # copy rendered file to the destination
                shutil.copy(rendered_file,this_file['dest']) 

        else:

            raise FileError( "%s file deploy was not performed. Source file is missing"%source_path )

def _load_dirs(directories, service_parmeters):

    # assume the directory path is relative to the location
    # of the service descriptor file (just like Dockerfile!)
    servicefile_path = get_variable(service_parmeters,"servicefile-path","")

    for this_idir in directories:

        # render intrinsics in the file dictionary
        this_dir = apply_fxn(this_idir, service_parmeters)      

        source_path = os.path.join(servicefile_path,this_dir['src'])

        # render files into a 'tmp' directory under the servicefile dir
        rendered_dir_path = os.path.join(servicefile_path,'tmp',this_dir['src'])

        if os.path.exists(source_path):

            # replace any service parmeters variables in the file body and return the 
            # "rendered" file contents as a string
            apply_templates_in_dir(source_path, service_parmeters, rendered_dir_path)

            # if destination is s3 bucket
            if is_s3_destination(this_dir['dest']):

                # sync directories to s3 destination
                sync_dir_to_s3( rendered_dir_path, this_dir['dest'])

            # if destination is another local dir (mostly used for testing)
            else:

                # clear destination dir if it exists
                if os.path.exists(this_dir['dest']):
                    shutil.rmtree(this_dir['dest'])

                # recursively copy tmp dir to the destination
                shutil.copytree(rendered_dir_path,this_dir['dest']) 
        else:

            raise FileError( "%s directory deploy was not performed. Source dir is missing"%source_path )


# returns true if file to be loaded is configured for an s3 destination
def is_s3_destination( destination ):

    s3_destination = False

    # S3 destinations are URL's with s3 as the scheme
    # Use this to detect an S3 destination

    # attempt to parse the destination as a URL
    url_parts = urlparse.urlparse(destination)

    if (url_parts and url_parts.scheme and url_parts.scheme == 's3'):

        s3_destination = True

    return s3_destination

# cp a file to an s3 bucket
# raises an Error if source file does not exists
# or if s3 cp fails
def cp_file_to_s3(source_file, destination_s3_url):

    # make sure source file exists
    if os.path.exists(source_file):            

        # form aws cp command for this file
        aws_cmd = "aws s3 cp %s %s"%( source_file, destination_s3_url)

        try:
            subprocess.check_output( aws_cmd , stderr=subprocess.STDOUT, shell=True )

        except subprocess.CalledProcessError as e:
            raise FileError("Error copying file to s3 destination: %s"%e)

    else:
        raise FileError("Source file %s does not exist"%source_file)

# sync a directory to an s3 bucket
# raises an Error if source dir does not exists
# or if s3 sync fails
def sync_dir_to_s3(source_dir, destination_s3_url):

    # make sure source file exists
    if os.path.exists(source_dir):            

        # form aws sync command for this directory
        # use --delete option to remove any files or directories already in s3 
        # destination that aren't in source_dir
        aws_cmd = "aws s3 sync %s %s %s"%( source_dir, destination_s3_url,"--delete")

        try:
            subprocess.check_output( aws_cmd , stderr=subprocess.STDOUT, shell=True )

        except subprocess.CalledProcessError as e:
            raise FileError("Error copying directory to s3 destination: %s"%e)

    else:
        raise FileError("Source directory %s does not exist"%source_dir)

# Get the ip addresses of ec2 instances in a stack identified by stack_name
# with a name containing name_search_string.
# If no name_search_string provided, returns IP addresses of all stack EC2 instances
def get_ec2_ips( stack_name , name_search_string=""):

    # filters for stack_id in cloudformation tag
    filters = [{'Name':"tag:aws:cloudformation:stack-name", 'Values' : [stack_name]}]

    # if specifying a Name, filter on that name
    if name_search_string:
        filters.append({'Name':"tag:Name", 'Values' : [name_search_string]})

    #pull response with instances matching filters
    client = boto3.client('ec2')
    instances = client.describe_instances(Filters=filters)

    # get the private ip address of instances that are running
    ips = jmespath.search("Reservations[?Instances[?State.Name=='running']].Instances[*].PrivateIpAddress", instances)

    # because the of the reservations in the outer layer, the search above will return 
    # the IP array in a out array, e.g.
    # [[ip1, ip2, etc.]]

    # we need to get rid of outer array
    return ips[0]

# get the RDS endpoints associated with a stack
def get_rds_endpoints( stack_name ):

    endpoints = []

    # get the resources associated with the stack
    cloudformation = boto3.client('cloudformation')
    resources = cloudformation.describe_stack_resources(StackName=stack_name)

    rds_id = ""

    if 'StackResources' in resources:

        for resource in resources['StackResources']:

            if resource['ResourceType'] == 'AWS::RDS::DBInstance':

                rds_id = resource['PhysicalResourceId']

    if rds_id:

        client = boto3.client('rds')
        instances = client.describe_db_instances(DBInstanceIdentifier=rds_id)

        endpoints = jmespath.search("DBInstances[*].Endpoint.{Address: Address, Port: Port}", instances)

    return endpoints

def get_rds_instance_ids( stack_name ):

    instances_ids = []

    # get the resources associated with the stack
    cloudformation = boto3.client('cloudformation')
    resources = cloudformation.describe_stack_resources(StackName=stack_name)

    rds_id = ""

    if 'StackResources' in resources:

        for resource in resources['StackResources']:

            if resource['ResourceType'] == 'AWS::RDS::DBInstance':

                rds_id = resource['PhysicalResourceId']

    if rds_id:

        client = boto3.client('rds')
        instances = client.describe_db_instances(DBInstanceIdentifier=rds_id)

        instances_ids = jmespath.search("DBInstances[*].DBInstanceIdentifier", instances)

    return instances_ids    

# get the name of the elastic cache endpoint associated with a stack
def get_cache_endpoint( stack_name ):

    endpoint = {}

    # get the resources associated with the stack
    cloudformation = boto3.client('cloudformation')
    resources = cloudformation.describe_stack_resources(StackName=stack_name)

    cache_id = ""

    if 'StackResources' in resources:

        for resource in resources['StackResources']:

            if resource['ResourceType'] == 'AWS::ElastiCache::ReplicationGroup':

                cache_id = resource['PhysicalResourceId']

    if cache_id:

        client = boto3.client('elasticache')
        response = client.describe_replication_groups(ReplicationGroupId=cache_id)

        if ('ReplicationGroups' in response and len(response['ReplicationGroups'])>0):

            this_rep_group = response['ReplicationGroups'][0]

            for node in this_rep_group['NodeGroups']:

                if 'PrimaryEndpoint' in node:

                    endpoint = node['PrimaryEndpoint']

    return endpoint    

# get the subnets associated with an auto-scaling groups
def get_asg_subnet_ids( asg_name ):

    #pull response with instances matching filters
    client = boto3.client('autoscaling')
    response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

    if response['AutoScalingGroups']:
        asg = response['AutoScalingGroups'][0]
    else:
        asg = {}

    subnet_ids = []

    if asg:
        subnet_id_str = asg['VPCZoneIdentifier']
        subnet_ids = subnet_id_str.split(',')
        
    return subnet_ids  

# get the iam role associated with an auto-scaling groups
def get_stack_iam_role( params ):

    asg_name = get_resource_name(params,'asg')

    #pull response with instances matching filters
    client = boto3.client('autoscaling')
    response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

    if response['AutoScalingGroups']:
        asg = response['AutoScalingGroups'][0]
        launchConfigName = asg['LaunchConfigurationName']
    else:
        launchConfigName = ""

    iam_role = ""

    if launchConfigName:
        response = client.describe_launch_configurations(LaunchConfigurationNames=[launchConfigName])

        if response['LaunchConfigurations']:
            iam_role = response['LaunchConfigurations'][0]['IamInstanceProfile']
        
    return iam_role      

# get the ssh key associated with an auto-scaling groups
def get_stack_ssh_keys( params ):

    asg_name = get_resource_name(params,'asg')

    #pull response with instances matching filters
    client = boto3.client('autoscaling')
    response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

    if response['AutoScalingGroups']:
        asg = response['AutoScalingGroups'][0]
        launchConfigName = asg['LaunchConfigurationName']
    else:
        launchConfigName = ""

    ssh_key = ""

    if launchConfigName:
        response = client.describe_launch_configurations(LaunchConfigurationNames=[launchConfigName])

        if response['LaunchConfigurations']:
            ssh_key = response['LaunchConfigurations'][0]['KeyName']
        
    return ssh_key   

# get the ssl cert associated with an elb
def get_stack_ssl_cert( params ):

    ielb_name = get_resource_name(params,'i-elb')
    eelb_name = get_resource_name(params,'e-elb')

    #pull response with instances matching filters
    client = boto3.client('elb')
    response = client.describe_load_balancers(LoadBalancerNames=[ielb_name,eelb_name])

    if response['LoadBalancerDescriptions']:
        elb = response['LoadBalancerDescriptions'][0]
    else:
        elb = {}

    ssl_cert = ""

    if elb:
        ssl_certs = jmespath.search('[*].Listener.SSLCertificateId',elb['ListenerDescriptions'])
        if (ssl_certs and len(ssl_certs)==1):
            ssl_cert = ssl_cert[0]
        
    return ssl_cert     

# returns true if an existing stack has external (public) access
def stack_has_external_access( params ):

    external_access = False

    eelb_name = get_resource_name(params,'e-elb')

    #pull response with instances matching filters
    client = boto3.client('elb')
    response = client.describe_load_balancers(LoadBalancerNames=[eelb_name])

    if response['LoadBalancerDescriptions']:
        elb = response['LoadBalancerDescriptions'][0]
    else:
        elb = {}

    # if the e-elb was found, stack provides external access
    if elb:
        external_access = True

    return external_access

# get vpc associated with an existing stack
def get_stack_vpc( params ):

    stack_name = get_stack_name(params)

    vpc_id = ""

    if stack_name:

        # get the stack
        cloudformation = boto3.client('cloudformation')

        try:
            stack = cloudformation.describe_stacks(StackName=stack_name)

            # get the first stack's 'stack id'
            stack_id = stack['Stacks'][0]['StackId']

            # filters for stack_id in cloudformation tag
            filters = [{'Name':"tag:aws:cloudformation:stack-id", 'Values' : [stack_id]}]

            #pull response with instances matching filters
            client = boto3.client('ec2')

            reservations = client.describe_instances(Filters=filters)

            intances = jmespath.search('Reservations[*].Instances',reservations)

            if len(intances)>=1:

                # use the vpd id of the first instance
                # print intances[0][0]
                vpc_id = intances[0][0]['VpcId']

                vpcs = client.describe_vpcs(VpcIds=[vpc_id])

                if 'Vpcs' in vpcs and len(vpcs['Vpcs'])==1:
                    vpc =  vpcs['Vpcs'][0]
                    vpc_id = vpc["VpcId"]

        except ClientError as e:
            print "existing stack not found"

        return vpc_id   

# get the subnets associated with an internal load balancer
def get_elb_subnet_ids( load_balancer_name ):

    #pull response with instances matching filters
    client = boto3.client('elb')
    response = client.describe_load_balancers(LoadBalancerNames=[load_balancer_name])

    if response['LoadBalancerDescriptions']:
        elb = response['LoadBalancerDescriptions'][0]
    else:
        elb = {}

    subnet_ids = []

    if elb:
        subnet_ids = elb['Subnets']
        
    return subnet_ids

def get_stack_param_value( stack_name , stack_param_name ):
    
    client = boto3.client('cloudformation')

    response = client.describe_stacks(StackName=stack_name)
    
    if response['Stacks']:
        stack = response['Stacks'][0]
    else:
        stack = {}

    value = ""

    if (stack and 'Parameters' in stack):
        for param in stack['Parameters']:
            if param['ParameterKey'] == stack_param_name:
                value = param['ParameterValue'] 
        
    return value

# get the value from a tag
def get_stack_tag_value( service_params , stack_tag_name ):

    stack_name = get_stack_name(service_params)
    
    client = boto3.client('cloudformation')

    response = client.describe_stacks(StackName=stack_name)
    
    if response['Stacks']:
        stack = response['Stacks'][0]
    else:
        stack = {}

    value = ""

    if (stack and 'Tags' in stack):
        for param in stack['Tags']:
            if param['Key'] == stack_tag_name:
                value = param['Value'] 
        
    return value
   