from django_lare import VERSION


class Lare(object):

    enabled = False
    current_namespace = ""
    previous_namespace = ""
    version = VERSION
    supported_version = "1.0.0"

    def __init__(self, request):
        super(Lare, self).__init__()
        if 'HTTP_X_LARE' in request.META:
            if 'HTTP_X_LARE_VERSION' in request.META:
                frontend_version = request.META['HTTP_X_LARE_VERSION']
                frontend_versions = frontend_version.split('.')
                supported_versions = self.supported_version.split('.')
                i = 0
                while i < len(supported_versions):
                    if frontend_versions[i] < supported_versions[i]:
                        self.enabled = False
                        return
                    i += 1
            self.enabled = True
            self.previous_namespace = request.META['HTTP_X_LARE']

    def set_current_namespace(self, namespace):
        self.current_namespace = namespace

    def get_current_namespace(self):
        return self.current_namespace

    def is_enabled(self):
        return self.enabled

    def get_matching_count(self, extension_namespace=None):
        if not self.enabled:
            return 0
        if extension_namespace is None:
            extension_namespace = self.current_namespace

        matching_count = 0
        previous_namespaces = self.previous_namespace.split('.')
        extension_namespaces = extension_namespace.split('.')

        while matching_count < len(previous_namespaces) and matching_count < len(extension_namespaces):
            if previous_namespaces[matching_count] == extension_namespaces[matching_count]:
                matching_count += 1
            else:
                break
        return matching_count

    def matches(self, extension_namespace=None):
        if extension_namespace is None:
            extension_namespace = self.current_namespace
        return self.get_matching_count(extension_namespace) == len(extension_namespace.split('.'))
