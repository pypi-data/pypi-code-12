import os

from pypicloud_client.http import request_factory


class PypicloudClient(object):
    """Pypicloud API client, the client can e set ny environment variables.

    Args:
        kwargs (dict) :
            user (str): User for basic authentication
            password (str): Password for basic authentication
            host (str): Pypicloud host

    """
    def __init__(self, **kwargs):
        self.host = kwargs.get("host", os.environ.get("PYPICLOUD_HOST", None))
        self.auth = (
            kwargs.get("user", os.environ.get("PYPICLOUD_USER", None)),
            kwargs.get("password", os.environ.get("PYPICLOUD_PASSWORD", None))
        )

        if self.host is None:
            raise ValueError("host have to be set, not equal to {0}".format(self.host))

        if None in self.auth:
            raise ValueError("auth have to be set, not equal to {0}".format(self.auth))

    def get_versions(self, package):
        """Get the wheel versions of an package, ordered by date from most recent to least recent.

        Args:
            package: Package whose versions to get

        Returns:
            list of dict: List of package info.
        """
        endpoint = "/api/package/{package}/".format(package=package)
        versions = request_factory(self.host, "GET", endpoint, auth=self.auth)
        return sorted(versions["packages"], key=lambda pkg: pkg["last_modified"], reverse=True)

    def delete_package(self, package, version):
        """Delete package ona specific version

            Args:
                package (str): the package name
                version (str): the package version to delete
        """
        for target in [pkg for pkg in self.get_versions(package) if pkg["version"] == version]:
            endpoint = "api/package/{0}/{1}".format(package, target["filename"])
            request_factory(self.host, "DELETE", endpoint, auth=self.auth)
