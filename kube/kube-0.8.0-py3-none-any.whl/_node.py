"""Interface for node resources."""

import collections
import enum
import ipaddress

import pyrsistent

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


class NodeView(_base.ViewABC):
    """View of all the Node resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.  This is here for the :class:`kube.ViewABC`
       compatibility but can not be used for the NodeList resource.  A
       :class:`kube.NamespaceError` is raised when this is not
       ``None``.
    :type namespace: NoneType

    :raises kube.NamespaceError: If instantiated using a namespace.

    :ivar cluster: The :class:`kube.Cluster` instance.
    """

    def __init__(self, cluster, namespace=None):  # pylint: disable=super-init-not-called
        if namespace is not None:
            raise _error.NamespaceError(
                'NodeList does not support namespaces')
        self.cluster = cluster
        self.namespace = None

    def __iter__(self):
        """Iterator over all Node resource items in the cluster.

        :raises kube.APIError: For errors from the k8s API server.
        """
        data = self.cluster.proxy.get('nodes')
        for item in data['items']:
            yield NodeItem(self.cluster, item)

    @property
    def kind(self):
        """The kind of the underlying Kubernetes list resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.NodeList

    def fetch(self, name, namespace=None):
        """Retrieve an individual node by name.

        This returns the current verison of the resource item.

        :param str name: The name of the node to retrieve.
        :param str namespace: Must be *None* or a
           :class:`kube.NamespaceError` is raised.  Here only for
           compatibility with the ABC.

        :return: A single :class:`kube.NodeItem` instance.
        :raises LookupError: If the node does not exist.
        :raises kube.APIError: For errors from the k8s API server.
        :raises kube.NamespaceError: If a namespace is used.
        """
        if namespace is not None:
            raise _error.NamespaceError(
                'NodeList does not support namespaces')
        data = _util.fetch_resource(self.cluster, 'nodes', name)
        return NodeItem(self.cluster, data)

    def filter(self, *, labels=None, fields=None):
        """Return an iterable of a subset of the resources.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: An iterator of :class:`kube.ItemABC` instances
           of the correct type for the resrouce.

        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: for errors from the k8s API server.
        """
        data_iter = _util.filter_list(self.cluster, 'nodes',
                                      labels=labels, fields=fields)
        for item in data_iter:
            yield NodeItem(self.cluster, item)

    def watch(self):
        """Watch the NodeList of this view for changes to items.

        Whenever one of the resources items in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :retruns: An iterator of :class:`kube.WatchEvent` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.NodeItem`.

        :raises kube.APIError: For errors from the k8s API server.
        """
        nodelist = self.cluster.proxy.get('nodes')
        version = nodelist['metadata']['resourceVersion']
        jsonwatcher = self.cluster.proxy.watch('nodes', version=version)
        return _watch.ResourceWatcher(self.cluster, jsonwatcher, NodeItem)


class AddressType(enum.Enum):
    """Enumeration of the address types."""
    ExternalIP = 'ExternalIP'
    InternalIP = 'InternalIP'
    Hostname = 'Hostname'


class NodeItem(_base.ItemABC):
    """A node in the Kubernetes cluster.

    See http://kubernetes.io/docs/admin/node/ for details.

    :param cluster: The cluster this node belongs to.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :ivar cluster: The :class:`kube.Cluster` this node belongs to.

    :ivar raw: The raw decoded JSON object as returned by the API
       server.  This is a :class:`pyrsistent.PMap` instance.
    """
    _Address = collections.namedtuple('Address', ['type', 'addr'])

    def __init__(self, cluster, raw):  # pylint: disable=super-init-not-called
        self.cluster = cluster
        self.raw = raw

    @property
    def kind(self):
        """The Kubernetes resource kind of this resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.Node

    @property
    def meta(self):
        """The node's metadata as a :class:`kube.meta.ObjectMeta` instance.

        This provides access to the node's name, labels etc.
        """
        return _meta.ObjectMeta(self)

    def spec(self):
        """The spec of this node's resource item.

        This is the raw, decoded JSON data representing the spec of
        this node.
        """
        return pyrsistent.thaw(self.raw['spec'])

    @property
    def addresses(self):
        """An iterator of the addresses for this node.

        Each address is a namedtuple with ``(type, addr)`` as fields.
        Known types are in the :class:`kube.AddressType` enumeration.

        An empty list is returned if there are not yet any addresses
        associated with the node.
        """
        status = self.raw.get('status', {})
        for raw in status.get('addresses', []):
            type_ = AddressType(raw['type'])
            addr = ipaddress.ip_address(raw['address'])
            yield self._Address(type_, addr)

    @property
    def capacity(self):
        """The capacity of the node.

        CPU is expressed in cores and can use fractions of cores,
        while memory is expressed in bytes.
        """
        # See http://kubernetes.io/v1.1/docs/design/resources.html for
        # details on resources usage.  This needs to deal with custom
        # resources as well.  The current stub implementation does not
        # match well.
        raise NotImplementedError

    @property
    def conditions(self):
        """List of conditions."""
        raise NotImplementedError

    def watch(self):
        """Watch the node for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :returns: An iterator of :class:`kube.WatchEvents` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.NodeItem` instance.
        :raises kube.APIError: For errors from the k8s API server.
        """
        return _util.watch_item(self)
