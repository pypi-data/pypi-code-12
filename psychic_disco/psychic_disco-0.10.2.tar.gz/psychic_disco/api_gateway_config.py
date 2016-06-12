import re

import boto3

console = boto3.client('apigateway')


def fetch_api_by_name(api_name):
    """ Fetch an api record by its name """
    api_records = console.get_rest_apis()['items']
    matches = filter(lambda x: x['name'] == api_name, api_records)
    if not matches:
        return None
    return matches[0]


def fetch_resources_by_api(api_id):
    """ Fetch all resources for an apigateway rest api """
    return console.get_resources(restApiId=api_id)['items']


def fetch_resource(api_id, resource_id):
    """ Fetch extra metadata for this particular resource """
    return console.get_resource(restApiId=api_id, resourceId=resource_id)


def fetch_method(api_id, resource_id, verb):
    """ Fetch extra metadata for this particular method """
    return console.get_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=verb)


def lambda_arn_from_method_integration_arn(int_arn):
    pattern = '.*functions/(.*)/invocations'
    matches = re.match(pattern, int_arn)
    return matches.group(1)


def lambda_name_from_lambda_arn(lambda_arn):
    return lambda_arn.split(':')[-1]


def fetch_root_resource_for_api(api_id):
    records = console.get_resources(restApiId=api_id)['items']
    for resource in records:
        if resource['path'] == '/':
            return resource
