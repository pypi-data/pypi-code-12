"""Interface for namespaces."""

import enum

import pyrsistent

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


class NamespaceView(_base.ViewABC):
    """View of all the Namespace resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.  This is here for the :class:`kube.ViewABC`
       compatibility, namespaces can not be used for the NamespaceList
       resource.  A :class:`kube.NamespaceError` is raised when this
       is not ``None``.
    :type namespace: NoneType

    :raises kube.NamespaceError: If instantiated using a namespace.

    :ivar cluster: the :class:`kube.Cluster` instance.
    """

    def __init__(self, cluster, namespace=None):  # pylint: disable=super-init-not-called
        if namespace is not None:
            raise _error.NamespaceError(
                'NamespaceList does not support namespaces')
        self.cluster = cluster
        self.namespace = None

    def __iter__(self):
        """Iterate over all Namespace resource items in the cluster.

        :raises kube.APIError: For errors from the k8s API server.
        """
        data = self.cluster.proxy.get('namespaces')
        for item in data['items']:
            yield NamespaceItem(self.cluster, item)

    @property
    def kind(self):
        """The kind of the underlying Kubernetes list resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.NamespaceList

    def fetch(self, name, namespace=None):
        """Retrieve an individual Namespace resource item by name.

        This returns the current verison of the resource item.

        :param str name: The name of the namespace resource item to
           retrieve.
        :param str namespace: Must be *None* or a
           :class:`kube.NamespaceError` is raised.  Here only for
           compatibility with the ABC.

        :returns: A :class:`kube.NamespaceItem` instance.
        :raises LookupError: If the namespace does not exist.
        :raises kube.APIError: For errors from the k8s API server.
        :raises kube.NamespaceError: If a namespace is used.
        """
        if namespace is not None:
            raise _error.NamespaceError(
                'NodeList does not support namespaces')
        data = _util.fetch_resource(self.cluster, 'namespaces', name)
        return NamespaceItem(self.cluster, data)

    def filter(self, *, labels=None, fields=None):
        """Get a filtered iterator of namespaces.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: An iterator of :class:`NamespaceItem` instances
            which match the given selector.
        :raises ValueError: if an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: For errors from the k8s API server.
        """
        data_iter = _util.filter_list(self.cluster, 'namespaces',
                                      labels=labels, fields=fields)
        for data in data_iter:
            yield NamespaceItem(self.cluster, data)

    def watch(self):
        """Watch the NamespaceList of this view for changes to items.

        Whenever one of the Namespace resource items in the view
        changes a new :class:`kube.WatchEvent` instance is yielded.
        You can currently not control from "when" resources are being
        watched, other then from "now".  So be aware of any race
        conditions with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances
           where the :attr:`kube.WatchEvent.item` attribute will be a
           :class:`kube.NamespaceItem`.
        :raise kube.APIError: For errors from the k8s API server.
        """
        nslist = self.cluster.proxy.get('namespaces')
        version = nslist['metadata']['resourceVersion']
        jsonwatcher = self.cluster.proxy.watch('namespaces', version=version)
        return _watch.ResourceWatcher(self.cluster, jsonwatcher, NamespaceItem)


class NamespacePhase(enum.Enum):
    """Enumeration of all possible namespace phases.

    This is aliased to :attr:`NamespaceResource.NamespacePhase`
    for convenience.
    """
    Active = 'Active'
    Terminating = 'Terminating'


class NamespaceItem(_base.ItemABC):
    """A namespace in the Kubernetes cluster.

    See http://kubernetes.io/docs/admin/namespaces/ for details.

    :cvar NamespacePhase: Convenience alias of :class:`NamespacePhase`.

    :ivar cluster: the :class:`kube.Cluster` instance.
    :ivar raw: the raw JSON-decoded representation of the namespace.
    """

    NamespacePhase = NamespacePhase

    def __init__(self, cluster, raw):  # pylint: disable=super-init-not-called
        self.cluster = cluster
        self.raw = raw

    @property
    def kind(self):
        """The kind of the underlying Kubernetes resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.Namespace

    @property
    def meta(self):
        """Namespace's metadata as a :class:`kube.ObjectMeta`."""
        return _meta.ObjectMeta(self)

    def spec(self):
        """A copy of the spec of this namespace's resource.

        This is the raw, decoded JSON data representing the spec of
        this namespace.
        """
        return pyrsistent.thaw(self.raw['spec'])

    @property
    def phase(self):
        """Phase of the namespace as a :class:`kube.NamespacePhase`."""
        return NamespacePhase(self.raw['status']['phase'])

    def watch(self):
        """Watch the namespace for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :retruns: An iterator of :class:`kube.WatchEvents` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.NamespaceItem` instance..
        :raises kube.APIError: For errors from the k8s API server.
        """
        return _util.watch_item(self)
