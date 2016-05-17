"""Tools to work with a Kubernetes cluster.

This module contains the toplevel tools to work with a Kubernets
cluster and it's API server.
"""

import urllib.parse

import requests

from kube import _error
from kube import _namespace
from kube import _node
from kube import _pod
from kube import _replicaset
from kube import _secret
from kube import _service
from kube import _util
from kube import _watch


class Cluster:
    """A Kubernetes cluster.

    The entrypoint to control a Kubernetes cluster.  There is only one
    connection mechanism, which is via a local API server proxy.  This
    is normally achieved by running ``kubectl proxy``.

    :param str url: The URL of the API server.

    :ivar proxy: A helper class to directly access the API server. An
        instance of :class:`kube.APIServerProxy` helper class.
    :ivar nodes: A :class:`kube.NodeView` instance.
    """

    def __init__(self, url='http://localhost:8001/api/'):
        if not url.endswith('/'):
            url += '/'
        api_url = urllib.parse.urljoin(url, 'v1/')
        self.proxy = APIServerProxy(api_url)
        self.namespaces = _namespace.NamespaceView(self)
        self.nodes = _node.NodeView(self)
        self.pods = _pod.PodView(self)
        self.replicasets = _replicaset.ReplicaSetView(self)
        self.services = _service.ServiceView(self)
        self.secrets = _secret.SecretView(self)

    def close(self):
        """Close and clean up underlying resources."""
        self.proxy.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_val, exc_type, traceback):
        self.close()


class APIServerProxy:
    """Helper class to directly communicate with the API server.

    Since most classes need to communicate with the Kubernetes
    cluster's API server in a common way this class helps take care of
    the common logic.  It also keeps the requests session alive to
    enable connection pooling to the API server.

    :param str base_url: The URL of the API, including the API version.
    """

    def __init__(self, base_url='http://localhost:8001/api/v1/'):
        if not base_url.endswith('/'):
            base_url += '/'
        self._base_url = base_url
        self._session = requests.Session()

    def close(self):
        """Close underlying connections.

        Once the proxy has been closed then the it can no longer be used
        to issue further requests.
        """
        self._session.close()

    def urljoin(self, *path):
        """Wrapper around urllib.parse.urljoin for the configured base URL.

        :param path: Individual relative path components, they will be
           joined using "/".  None of the path components should
           include a "/" separator themselves.
        """
        return urllib.parse.urljoin(self._base_url, '/'.join(path))

    def get(self, *path, **params):
        """HTTP GET the relative path from the API server.

        :param str path: Individual relative path components, they
           will be joined using "/".  None of the path components
           should include a "/" separator themselves.
        :param dict params: Extra query parameters for the URL of the
           GET request as a dictionary of strings.

        :returns: The decoded JSON data.
        :rtype: pyrsistent.PMap

        :raises kube.APIError: If the response status is not 200 OK.
        """
        url = self.urljoin(*path)
        response = self._session.get(url, params=params)
        if response.status_code != 200:
            raise _error.APIError(response, 'Failed to GET {}'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def post(self, *path, json=None, **params):
        """HTTP POST to the relative path on the API server.

        :param path: Individual relative path components, they will be
           joined using :meth:`urljoin`.
        :type path: str
        :param json: The body to post, which will be JSON-encoded
           before posting.
        :type json: collections.abc.Mapping
        :param params: Extra query parameters for the URL of the POST
           request.
        :type params: str

        :returns: The decoded JSON data.
        :rtype: pyrsistent.PMap

        :raises kube.APIError: If the response status is not 201
           Created.
        """
        url = self.urljoin(*path)
        response = self._session.post(url, json=json, params=params)
        if response.status_code != 201:
            raise _error.APIError(response, 'Failed to POST {}'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def delete(self, *path, json=None, **params):
        """HTTP DELETE to the relative path on the API server.

        :param path: Individual relative path components, they will be
           joined using :meth:`urljoin`.
        :type path: str
        :param json: The body, which will be JSON-encoded before
           posting.
        :type json: collections.abc.Mapping
        :param params: Extra query parameters for the URL of the
           DELETE request.
        :type params: str

        :returns: The decoded JSON data.
        :rtype: pyrsistent.PMap

        :raises kube.APIError: If the response status is not 200 OK.
        """
        url = self.urljoin(*path)
        response = self._session.delete(url, json=json, params=params)
        if response.status_code != 200:
            raise _error.APIError(response, 'Failed to DELETE {}'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def patch(self, *path, patch=None):
        """HTTP PATCH as application/strategic-merge-patch+json.

        This allows using the Strategic Merge Patch to patch a
        resource on the Kubernetes API server.

        :param str path: Individual relative path components, they
           will be joined using "/".  None of the path components
           should include a "/" separator themselves, unless you only
           provide one component which will be joined to the base URL
           using :func:`urllib.parse.urljoin`.  This case can be
           useful to use the links provided by the API itself
           directly, e.g. from a resource's ``metadata.selfLink``
           field.
        :param dict patch: The decoded JSON object with the patch
           data.

        :returns: The decoded JSON object of the resource after
           applying the patch.

        :raises APIError: If the response status is not 200 OK.
        """
        url = self.urljoin(*path)
        headers = {'Content-Type': 'application/strategic-merge-patch+json'}
        response = self._session.patch(url, headers=headers, json=patch)
        if response.status_code != 200:
            raise _error.APIError(response, 'Failed to PATCH {}:'.format(url))
        else:
            return response.json(cls=_util.ImmutableJSONDecoder)

    def watch(self, *path, version=None, fields=None):
        """Watch a list resource for events.

        This issues a request to the API with the ``watch`` query
        string parameter set to ``true`` which returns a chunked
        response.  An iterator is returned which continuously reads
        from the response, yielding received lines as bytes.

        :param path: The URL path to the resource to watch. See
            :meth:`urljoin`.
        :param str version: The resource version to start watching from.
        :param dict fields: A dict of fields which must match their
           values.  This is a limited form of the full fieldSelector
           format, it is limited because filtering is done at client
           side for consistecy.

        :returns: An special iterator which allows non-blocking
           iterating using a ``.next(timeout) method.  Using it as a
           normal iterator will result in blocking behaviour.
        :rtype: :class:`LineWatcher`.

        :raises APIError: If there is a problem with the API server.
        """
        return _watch.JSONWatcher(self, *path, version=version, fields=fields)
