
class Widget(object):
    def get_bundle(self):
        """
        Get the JS pack as a streaming object.
        Needs to be a stream.
        eg. pkg_resources.resource_stream(module, filename)

        :return: file like object
        """
        raise NotImplementedError()
