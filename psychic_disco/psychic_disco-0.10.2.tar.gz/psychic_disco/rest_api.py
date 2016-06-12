import psychic_disco.api_gateway_config as agc
from psychic_disco.rest_resource import RestResource


class RestApi(object):
    """ Model of an AWS API Gateway Rest API object. """

    apis_by_name = dict()
    """ Cache of API objects to ensure that there is
    a singleton for each actual API by name """

    def __init__(self, name):
        """ Not intended for external use. Call
        RestApi.find() method """
        self.name = name
        self.aws_id = None
        self.resources = dict()

    @classmethod
    def find(cls, api_name):
        """ Find or create an API model object by name """
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
            record = agc.fetch_root_resource_for_api(self.aws_id)
            root.aws_id = record['id']
        return root

    def _fetch_from_aws(self):
        record = agc.fetch_api_by_name(self.name)
        if record:
            self.aws_id = record['id']

    @property
    def exists_in_aws(self):
        return (self.aws_id is not None)

    def _fetch_resources(self):
        for record in agc.fetch_resources_by_api(self.aws_id):
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
            agc.console.create_rest_api(name=self.name)
            self._fetch_from_aws()
        self.root_resource.deploy()  # It's special
        for path in sorted(self.resources.keys()):
            resource = self.resources[path]
            resource.deploy()
        agc.console.create_deployment(
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
