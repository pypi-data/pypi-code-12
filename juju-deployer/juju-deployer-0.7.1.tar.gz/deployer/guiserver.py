"""Juju GUI server bundles deployment support.

The following functions are used by the Juju GUI server to validate
and start bundle deployments. The validate and import_bundle
operations represents the public API: they are directly called in the
GUI server bundles support code, which also takes care of handling any
exception they can raise.  Those functions are blocking, and therefore
the GUI server executes them in separate processes.  See
<https://code.launchpad.net/~juju-gui/charms/precise/juju-gui/trunk>.
"""

import os

from deployer.action.importer import Importer
from deployer.cli import setup_parser
from deployer.deployment import Deployment
from deployer.env.gui import GUIEnvironment
from deployer.utils import (
    DeploymentError,
    mkdir,
)


# This value is used by the juju-deployer Importer object to store charms.
# This directory is usually created in the machine where the Juju GUI charm is
# deployed the first time a bundle deployment is requested.
JUJU_HOME = '/var/lib/juju-gui/juju-home'


def get_default_guiserver_options():
    """Return the default importer options used by the GUI server."""
    # Options used by the juju-deployer.  The defaults work for us, except for
    # the ignore_errors flag.
    return setup_parser().parse_args(['--ignore-errors'])


class GUIDeployment(Deployment):
    """Handle bundle deployments requested by the GUI server."""

    def __init__(self, name, data, version):
        super(GUIDeployment, self).__init__(name, data, [], version=version)

    def _handle_feedback(self, feedback):
        """Raise a DeploymentError if the given feedback includes errors.

        The GUI server will catch and report failures propagating them through
        the WebSocket connection to the client.
        """
        for message in feedback.get_warnings():
            self.log.warning(message)
        if feedback.has_errors:
            # Errors are logged by the GUI server.
            raise DeploymentError(feedback.get_errors())


def _validate(env, bundle):
    """Bundle validation logic, used by both validate and import_bundle.

    This function receives a connected environment and the bundle as a YAML
    decoded object.
    """
    # Retrieve the services deployed in the Juju environment.
    env_status = env.status()
    env_services = set(env_status['services'].keys())
    # Retrieve the services in the bundle.
    bundle_services = set(bundle.get('services', {}).keys())
    # Calculate overlapping services.
    overlapping = env_services.intersection(bundle_services)
    if overlapping:
        services = ', '.join(overlapping)
        error = 'service(s) already in the environment: {}'.format(services)
        raise ValueError(error)


def validate(apiurl, username, password, bundle):
    """Validate a bundle."""
    env = GUIEnvironment(apiurl, username, password)
    env.connect()
    try:
        _validate(env, bundle)
    finally:
        env.close()


def import_bundle(apiurl, username, password, name, bundle, version, options):
    """Import a bundle.

    To connect to the Juju environment, use the given API URL, user name and
    password. The name and bundle arguments are used to deploy the bundle. The
    version argument specifies whether the given bundle content uses the
    legacy v3 or the new v4 bundle syntax. The given options are used to
    start the bundle deployment process.
    """
    env = GUIEnvironment(apiurl, username, password)
    deployment = GUIDeployment(name, bundle, version=version)
    importer = Importer(env, deployment, options)
    env.connect()
    # The Importer tries to retrieve the Juju home from the JUJU_HOME
    # environment variable: create a customized directory (if required) and
    # set up the environment context for the Importer.
    mkdir(JUJU_HOME)
    os.environ['JUJU_HOME'] = JUJU_HOME
    try:
        _validate(env, bundle)
        importer.run()
    finally:
        env.close()
