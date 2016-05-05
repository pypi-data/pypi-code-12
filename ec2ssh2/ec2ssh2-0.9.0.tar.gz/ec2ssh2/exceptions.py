class EC2SSH2Exception(Exception):
    pass


class InvalidInput(EC2SSH2Exception):
    def __init__(self, bad_input, explanation=''):
        super(EC2SSH2Exception, self).__init__(bad_input, explanation)


class UnsupportedMethod(EC2SSH2Exception):
    pass


class NoInstancesFound(EC2SSH2Exception, LookupError):
    pass
