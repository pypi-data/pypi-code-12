from boto3.session import Session
from nephoria.testconnection import TestConnection

class RegionContext():
    """
    Intended to help store and manage a give user's session, client, and test ops connections
    per given region.
    """
    def __init__(self, name, usercontext):
        """

        :param name: Name of this region
        :param usercontext: The usercontext used for this RegionContext's connections.
        """
        self.name = name
        self.usercontext = usercontext
        self.service_clients = {}
        self.service_ops = {}
        self._session = None
        self.log = usercontext.log

    def __repr__(self):
        name = self.name or "{0}(Default)".format(self.name)
        return "{0}:{1}".format(self.__class__.__name__, name)

    @property
    def session(self):
        """
        Return Boto3 session for this test region
        """
        if not self._session:
            self._session = Session(aws_access_key_id=self.usercontext.aws_access_key,
                                    aws_secret_access_key=self.usercontext.aws_secret_key,
                                    region_name=self.name)
        return self._session

    @session.setter
    def session(self, session):
        """
        Set the Boto3 session for this test region

        :param session: session (or None) to set for this region
        """
        if session is None:
            self._session = None
            return
        if not isinstance(session, Session):
            raise ValueError('Can not set session. Must be of type Session, got:"{0}/{1}"'
                             .format(session, type(session)))
        if session._session._credentials.access_key == self.usercontext.aws_access_key and \
                session._session._credentials.secret_key == self.usercontext.aws_secret_key:
            self._session = session
        else:
            raise ValueError('Can not reassign session. Access Key and/or Secret do not '
                             'match current user context')

    def get_client(self, service_name, endpoint_url=None, verify=False, *args, **kwargs):
        """
        Fetch the client interface for a particular service (ie 'ec2', 's3', 'iam', etc) for
        this region
        :param service_name: string representing the service. ie 'ec2', 'iam', 's3, etc..
        :param endpoint_url: service endpoint url
        :param verify:  Whether or not to verify SSL certificates
        :param args: optional positional args to be passed when fetching client
        :param kwargs: optional keyword args to be passed when fetching client
        """
        client = self.service_clients.get(service_name, None)
        if not client and endpoint_url:
            client = self.session.client(service_name, region_name=self.name,
                                         endpoint_url=endpoint_url,
                                         validate=verify, *args, **kwargs)
            self.service_clients[service_name] = client
        return client

    def get_service_ops(self, service_name):
        """
        Fetch the testops interface (ie ec2ops, iamops, s3ops) for a particular service if one
        has been created and registered with this region.
        :param service_name: string representing the service. ie 'ec2', 'iam', 's3, etc..
        """
        return self.service_ops.get(service_name, None)

    def set_service_ops(self, service_name, ops):
        """
        Set the ops interface (testconnection) for a given service_name for this region
        :param service_name: string representing the service. ie 'ec2', 'iam', 's3, etc..
        :param ops: The testops/testconnection for this service. ie 'ec2ops', 's3ops', etc
        """
        class_name = TestConnection.__class__.__name__
        if not service_name:
            raise ValueError('Service name not provided to set, got:"{0}"'.format(service_name))
        if ops is None:
            self.log.debug('Setting "{0}" to None'.format(service_name))
        elif not isinstance(ops, TestConnection):
            raise TypeError('Set "{0}" ops must be of type:"{1}", got:"{2}/{3}"'
                            .format(service_name, class_name, ops, type(ops)))
        self.service_ops[service_name] = ops
