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


def fetch_root_resource_for_api(api_id):
    records = console.get_resources(restApiId=api_id)['items']
    for resource in records:
        if resource['path'] == '/':
            return resource


class RestApi(object):
    apis_by_name = dict()

    def __init__(self, name):
        self.name = name
        self.aws_id = None
        self.resources = dict()

    @classmethod
    def find(cls, api_name):
        if api_name in cls.apis_by_name:
            return cls.apis_by_name[api_name]
        api = cls(api_name)
        api._fetch_from_aws()
        if api.exists_in_aws:
            api._fetch_resources()
        cls.apis_by_name[api_name] = api
        return api

    @property
    def root_resource(self):
        root = self.declare_resource('/')
        if not root.exists_in_aws:
            record = fetch_root_resource_for_api(self.aws_id)
            root.aws_id = record['id']
        return root

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

    def deploy(self):
        print "Deploying API: %s" % self.name
        self._fetch_from_aws()
        if not self.exists_in_aws:
            console.create_rest_api(name=self.name)
            self._fetch_from_aws()
        self.root_resource.deploy()  # It's special
        for path in sorted(self.resources.keys()):
            resource = self.resources[path]
            resource.deploy()
        console.create_deployment(
                restApiId=self.aws_id,
                stageName='master')

    def declare_route(self, verb, path, lambda_function):
        r = self.declare_resource(path)
        r.declare_route(verb, lambda_function)

    def declare_resource(self, path):
        if path not in self.resources:
            r = RestResource(path)
            r.api = self
            self.resources[path] = r
        return self.resources[path]


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

    @property
    def parent(self):
        if self.path == '/':
            return None
        else:
            parent_path = '/'.join(self.path.split('/')[0:-1]) or '/'
            return self.api.declare_resource(parent_path)

    @property
    def path_part(self):
        if self.parent:
            return self.path.replace(self.parent.path, '', 1)
        else:
            return self.path

    def deploy(self):
        print "\tDeploying Resource: %s" % self.path
        if not self.exists_in_aws:
            self.parent.deploy()
            response = console.create_resource(
                    restApiId=self.api.aws_id,
                    parentId=self.parent.aws_id,
                    pathPart=self.path_part)
            self.aws_id = response['id']
        for verb in self.methods:
            method = self.methods[verb]
            method.deploy()

    def declare_method(self, verb):
        if verb not in self.methods:
            m = RestMethod(verb)
            m.resource = self
            m.api = self.api
            self.methods[verb] = m
        return self.methods[verb]

    def declare_route(self, verb, lambda_function):
        m = self.declare_method(verb)
        m.declare_route(lambda_function)


class RestMethod(object):
    def __init__(self, verb):
        self.verb = verb
        self.resource = None
        self.api = None
        self.lambda_name = None
        self.lambda_function = None

    def declare_route(self, lf):
        self.lambda_function = lf
        self.lambda_name = lf.proper_name

    def fetch_from_aws(self):
        if (self.resource is None or self.api is None):
            msg = """I cannot possibly question AWS
            without knowing my resource and api ids"""
            raise Exception(msg)
        record = fetch_method(self.api.aws_id, self.resource.aws_id, self.verb)
        arn = record['methodIntegration']['uri']
        lambda_arn = lambda_arn_from_method_integration_arn(arn)
        self.lambda_name = lambda_name_from_lambda_arn(lambda_arn)

    @property
    def exists_in_aws(self):
        try:
            console.get_method(
                    restApiId=self.api.aws_id,
                    resourceId=self.resource.aws_id,
                    httpMethod=self.verb)
            return True
        except:
            return False

    @property
    def integration_uri(self):
        pattern = "arn:aws:apigateway:region:lambda:path/2015-03-31/functions/%s/invocations"  # noqa
        return pattern % self.lambda_function.arn

    def deploy(self):
        print "\t\tDeploying Method: %s" % self.verb
        should_put_integration = False
        if not self.exists_in_aws:
            should_put_integration = True
            console.put_method(
                    restApiId=self.api.aws_id,
                    resourceId=self.resource.aws_id,
                    httpMethod=self.verb,
                    authorizationType='NONE')
        if self.lambda_function:
            self.lambda_function.deploy()
        if should_put_integration:
            console.put_integration(
                    restApiId=self.api.aws_id,
                    resourceId=self.resource.aws_id,
                    httpMethod=self.verb,
                    type='AWS',
                    integrationHttpMethod=self.verb,
                    uri=self.integration_uri)
