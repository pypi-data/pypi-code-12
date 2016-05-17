"""Interface for ObjectMeta objects."""

import collections.abc

import pyrsistent

from kube import _util as util


class ObjectMeta:
    """Common metadata for API objects.

    :param resource: The object representing the Kubernetes resource which
       this metadata describes.
    :type resource: kube._base.ItemABC
    """

    def __init__(self, resource):
        self._resource = resource

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self._resource.raw['metadata'] ==
                    other._resource.raw['metadata'])  # pylint: disable=protected-access
        else:
            return NotImplemented

    @property
    def name(self):
        """The name of the object."""
        return self._resource.raw['metadata']['name']

    @property
    def namespace(self):
        """Namespace the object resides in, or ``None``."""
        try:
            return self._resource.raw['metadata']['namespace']
        except KeyError:
            return None

    @property
    def labels(self):
        """The labels as a :class:`ResourceLabels` instance."""
        return ResourceLabels(self._resource)

    @property
    def version(self):
        """The opaque resource version."""
        return self._resource.raw['metadata']['resourceVersion']

    @property
    def created(self):
        """The created timestamp."""
        return util.parse_rfc3339(
            self._resource.raw['metadata']['creationTimestamp'])

    @property
    def link(self):
        """A link to the resource itself.

        This is currently an absolute URL without the hostname, but
        you don't have to care about that.  The
        :class:`kube.APIServerProxy` will be just fine with it as it's
        ``path`` argument.
        """
        return self._resource.raw['metadata']['selfLink']

    @property
    def uid(self):
        """The Universal ID of the item.

        This is unique for this resource kind.
        """
        return self._resource.raw['metadata']['uid']


class ResourceLabels(collections.abc.Mapping):
    """The labels applied to an API resource.

    This allows introspecting the labels as a normal mapping and
    provides a few methods to directly manipulate the labels on the
    resource.
    """

    def __init__(self, resource):
        self._resource = resource
        self._data = resource.raw['metadata'].get('labels', pyrsistent.pmap())

    def __getitem__(self, name):
        return self._data[name]

    def __iter__(self):
        for key in self._data:
            yield key

    def __len__(self):
        return len(self._data)

    def set(self, key, value):
        """Set a (new) label.

        This will set or update the label's value on the resource.

        :returns: A new instance of the resource.
        :raises kube.APIError: If there is a problem with the API server.
        """
        raw = self._resource.cluster.proxy.patch(
            self._resource.meta.link,
            patch={'metadata': {'labels': {key: value}}},
        )
        return self._resource.__class__(self._resource.cluster, raw)

    def delete(self, key):
        """Delete a label.

        This will remove the label for a given key from the resource.

        :returns: A new instance of the resource.
        :raises kube.APIError: If there is a problem with the API server.
        """
        raw = self._resource.cluster.proxy.patch(
            self._resource.meta.link,
            patch={'metadata': {'labels': {key: None}}},
        )
        return self._resource.__class__(self._resource.cluster, raw)

    def __repr__(self):
        return '<Labels "{}">'.format(
            ','.join('{}={}'.format(k, v) for k, v in self.items()))
