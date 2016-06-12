import psychic_disco.api_gateway_config as agc
from psychic_disco.rest_method import RestMethod


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
        record = agc.fetch_resource(self.api.aws_id, self.aws_id)
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
            return self.path.replace(self.parent.path + "/", '', 1)
        else:
            return self.path

    def deploy(self):
        print "\tDeploying Resource: %s" % self.path
        if not self.exists_in_aws:
            self.parent.deploy()
            response = agc.console.create_resource(
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
