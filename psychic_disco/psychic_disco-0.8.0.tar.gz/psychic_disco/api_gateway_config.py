import boto3
import re

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


class RestApi(object):
    def __init__(self, name):
        self.name = name
        self.aws_id = None
        self.resources = dict()

    @classmethod
    def find(cls, api_name):
        api = cls(api_name)
        api._fetch_from_aws()
        if api.exists_in_aws:
            api._fetch_resources()
        return api

    def _fetch_from_aws(self):
        record = fetch_api_by_name(self.name)
        if record:
            self.aws_id = record['id']

    @property
    def exists_in_aws(self):
        return (self.aws_id is not None)

    def _fetch_resources(self):
        for record in fetch_resources_by_api(self.aws_id):
            path = record['path']
            if path not in self.resources:
                self.resources[path] = RestResource(path)
            resource = self.resources[path]
            resource.aws_id = record['id']
            resource.api = self
            resource.fetch_from_aws()


class RestResource(object):
    def __init__(self, path):
        self.path = path
        self.aws_id = None
        self.api = None
        self.methods = dict()

    @property
    def exists_in_aws(self):
        return (self.aws_id is not None and self.api is not None)

    def fetch_from_aws(self):
        if not self.exists_in_aws:
            raise Exception("Not enough info to query AWS for Rest Resource")
        record = fetch_resource(self.api.aws_id, self.aws_id)
        if 'resourceMethods' in record:
            for verb in record['resourceMethods']:
                if verb not in self.methods:
                    self.methods[verb] = RestMethod(verb)
                method = self.methods[verb]
                method.resource = self
                method.api = self.api
                method.fetch_from_aws()


class RestMethod(object):
    def __init__(self, verb):
        self.verb = verb
        self.resource = None
        self.api = None
        self.lambda_name = None
        self.lambda_function = None

    def fetch_from_aws(self):
        if (self.resource is None or self.api is None):
            msg = """I cannot possibly question AWS
            without knowing my resource and api ids"""
            raise Exception(msg)
        record = fetch_method(self.api.aws_id, self.resource.aws_id, self.verb)
        arn = record['methodIntegration']['uri']
        lambda_arn = lambda_arn_from_method_integration_arn(arn)
        self.lambda_name = lambda_name_from_lambda_arn(lambda_arn)
