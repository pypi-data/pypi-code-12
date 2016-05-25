import requests

class BuildkiteAuth(object):
    def set_parent(self, parent):
        self.parent_object = parent

    def access_token(self, t):
        self.token = t

    def url_parts(self):
        return []

    def url_parameters(self):
        return ["access_token=" + self.token]


class BuildkiteOrganizations(object):
    def __init__(self):
        self.organization = None

    def set_parent(self, parent):
        self.parent_object = parent

    def url_parts(self):
        rv = ["organizations"]
        if self.organization:
            rv.append(self.organization)
        return rv

    def url_parameters(self):
        return []

    def list(self):
        url = self.parent_object.build_request(('auth', 'organizations'))
        r = requests.get(url)
        return r.json()

    def set_organization(self, org):
        self.organization = org
        return self.parent_object


class BuildkitePipelines(object):
    def __init__(self):
        self.pipeline = None

    def set_parent(self, parent):
        self.parent_object = parent

    def url_parts(self):
        rv = ["pipelines"]
        if self.pipeline:
            rv.append(self.pipeline)
        return rv

    def url_parameters(self):
        return []

    def list(self):
        url = self.parent_object.build_request(('auth',
                                                'organizations',
                                                'pipelines'))
        r = requests.get(url)
        return r.json()

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
        return self.parent_object


class BuildkiteBuilds(object):
    def __init__(self):
        self.pipeline = None

    def set_parent(self, parent):
        self.parent_object = parent

    def url_parts(self):
        rv = ["builds"]
        if self.pipeline:
            rv.append(self.pipeline)
        return rv

    def url_parameters(self):
        return []

    # TODO: a protocol where if the sub-object (e.g. organization) doesn't
    # have a parameter it does something reasonable (stays out of the way).
    def list(self):
        url = self.parent_object.build_request(('auth', 'builds'))
        r = requests.get(url)
        return r.json()

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
        return self.parent_object


class Buildkite(object):
    def __init__(self):
        self.api_objects = {
            'auth': BuildkiteAuth(),
            'organizations': BuildkiteOrganizations(),
            'pipelines': BuildkitePipelines(),
            'builds': BuildkiteBuilds()
        }
        for k in self.api_objects:
            self.api_objects[k].set_parent(self)

    def build_request(self, url_pieces):
        url = self.url_parts()
        for piece in url_pieces:
            for part in self.api_objects[piece].url_parts():
                url = '/'.join((url, part))
        parameters = []
        for piece in url_pieces:
            for part in self.api_objects[piece].url_parameters():
                parameters.append(part)
        if parameters:
            url = url + '?' + ''.join(parameters)
        return url

    def url_parts(self):
        return "https://api.buildkite.com/v2"

    def url_parameters(self):
        return []

    # TODO: generate these from the api_objects map.
    def auth(self):
        return self.api_objects['auth']

    def organization(self):
        return self.api_objects['organizations']

    def pipelines(self):
        return self.api_objects['pipelines']

    def builds(self):
        return self.api_objects['builds']

