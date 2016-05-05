"""GUI server environment implementation.

The environment defined here is intended to be used by the Juju GUI server.
See <https://code.launchpad.net/~juju-gui/charms/precise/juju-gui/trunk>.
"""

from .go import GoEnvironment, EnvironmentClient
from ..utils import get_qualified_charm_url, parse_constraints


class GUIEnvironment(GoEnvironment):
    """A Juju environment for the juju-deployer.

    Add support for deployments via the Juju API and for authenticating with
    the provided credentials.
    """

    def __init__(self, endpoint, username, password):
        super(GUIEnvironment, self).__init__('gui', endpoint=endpoint)
        self._username = username
        self._password = password

    def connect(self):
        """Connect the API client to the Juju backend.

        This method is overridden so that a call to connect is a no-op if the
        client is already connected.
        """
        if self.client is None:
            self.client = EnvironmentClient(self.api_endpoint)
            self.client.login(self._password, user=self._username)

    def close(self):
        """Close the API connection.

        Also set the client attribute to None after the disconnection.
        """
        super(GUIEnvironment, self).close()
        self.client = None

    def deploy(
            self, name, charm_url, repo=None, config=None, constraints=None,
            num_units=1, force_machine=None, series=None):
        """Deploy a service using the API.

        Using the API in place of the command line introduces some limitations:
          - it is not possible to use a local charm/repository.

        The repo and series arguments are ignored but listed since the
        Importer always passes the value as a positional argument.

        """
        charm_url = get_qualified_charm_url(charm_url)
        constraints = parse_constraints(constraints)
        self.client.deploy(
            name, charm_url, config=config, constraints=constraints,
            num_units=num_units, machine_spec=force_machine)
