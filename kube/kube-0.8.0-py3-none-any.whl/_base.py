"""Some base classes and ABCs for kube.

While all implementations are supposed to at least register their
classes, subclassing is not really a aim.  With the exception of
:meth:`__repr__` most properties and methods are marked as abstract
and do not have a common implementation even if they could.  To share
code instead helper functions in ``kube._util`` should be used.
"""

import abc
import enum


class ViewABC(metaclass=abc.ABCMeta):
    """Represents a view to a collection of resources.

    All top-level resources in Kubernetes have a collection, resources
    of a ``*List`` kind, with some common functionality.  This ABC
    defines views to provide access to resources in collections in a
    uniform way.  Note that a view is not the same as the collection
    resource, e.g. collections resources have some metadata associated
    with them and exist at a particular point in time, they have a
    metadata.resourceVersion, which views do not have.

    It is always possible to create an instance of this without
    needing to do any requests to the real Kubernetes cluster.

    :param cluster: The cluster this resource list is part of.
    :type cluster: kube.Cluster
    :param namespace: The optional namespace this resource list is
       part of.  If the resource list is not part of a namespace this
       will be ``None`` which means it will be a view to all resources
       of a certain type, regardelss of their namespace.
    :type namespace: str

    :raises kube.NamespaceError: When a namespace is provided but the
       resource does not support one.

    :ivar kube.Cluster cluster: The cluster this resource list is part
       of.
    :ivar str namespace: The optional namespace this resource list is
       part of.  If the resource list is not part of a namespace this
       will be ``None``, including for resource lists which do not
       support namespaces.
    """

    @abc.abstractmethod
    def __init__(self, cluster, namespace=None):
        self.cluster = cluster
        self.namespace = namespace

    def __repr__(self):
        if self.namespace is None:
            return '<{0.__class__.__name__}>'.format(self)
        else:
            return ('<{0.__class__.__name__} namespace={0.namespace}>'
                    .format(self))

    @abc.abstractmethod         # pragma: nocover
    def __iter__(self):
        """Iterator of all resources in this collection.

        :raises kube.APIError: for errors from the k8s API server.
        """

    @abc.abstractproperty         # pragma: nocover
    def kind(self):
        """The kind of the underlying Kubernetes resource.

        This is a :class:`kube.Kind` enum.
        """

    @abc.abstractmethod         # pragma: nocover
    def fetch(self, name, namespace=None):
        """Retrieve the current version of a single resource item by name.

        If the view itself is associated with a namespace,
        ``self.namespace is not None``, then this will default to
        fetching the resource item from this namespace.  If the view
        is not associated with a namespace, ``self.namespace is
        None``, and the resource requires a namespace then a
        :class:`kube.NamespaceError` is raised.  Note that the
        ``default`` namespace is not automatically used in this case.

        :param str name: The name of the resource.
        :param str namespace: The namespace to fetch the resource
           from.

        :returns: A single instance representing the resource.

        :raises LookupError: If the resource does not exist.
        :raises kube.NamespaceError: For an invalid namespace, either
           because the namespace is required for this resource but not
           provided or the resource does not support namespaces and
           one was provided.
        :raises kube.APIError: For errors from the k8s API server.
        """

    @abc.abstractmethod         # pragma: nocover
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

        :returns: An iterator of :class:`kube.ItemABC` instances of
           the correct type for the resrouce which match the given
           selector.

        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: For errors from the k8s API server.
        """

    @abc.abstractmethod         # pragma: nocover
    def watch(self):
        """Watch for changes to any of the resources in the view.

        Whenever one of the resources in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances.

        :raises kube.NamespaceError: Whe the namespace no longer
           exists.
        :raises kube.APIError: For errors from the k8s API server.
        """


class ItemABC(metaclass=abc.ABCMeta):
    """Representation for a kubernetes resource.

    All resources have some common attributes and API which must match
    this ABC.

    :param cluster: The cluster this resource is bound to.
    :type cluster: kube.Cluster
    :param raw: The decoded JSON representing the resource.
    :type raw: dict

    :ivar cluster: The :class:`kube.Cluster` instance this resource is
       bound to.
    :ivar raw: The raw decoded JSON representing the resource.  This
       behaves like a dict but is actually an immutable view of the
       dict.
    """

    @abc.abstractmethod
    def __init__(self, cluster, raw):
        self.cluster = cluster
        self.raw = raw

    def fetch(self):
        """Fetch the current version of the resource item.

        This will return a new instance of the current resource item
        at it's latest version.  This is useful to see any changes
        made to the object since it was last retrieved.

        :returns: An instance of the relevant :class:`ItemABC`
           subclass.

        :raises kube.APIError: For errors from the k8s API server.
        """
        data = self.cluster.proxy.get(self.meta.link)
        return self.__class__(self.cluster, data)

    def __repr__(self):
        if self.meta.namespace is not None:
            return ('<{0.__class__.__name__} {0.meta.name} '  # pylint: disable=missing-format-attribute
                    'namespace={0.meta.namespace}>' .format(self))
        else:
            return '<{0.__class__.__name__} {0.meta.name}>'.format(self)  # pylint: disable=missing-format-attribute

    @abc.abstractproperty       # pragma: nocover
    def kind(self):
        """The Kubernetes resource kind of the resource.

        This is a :class:`kube.Kind` enum.
        """

    @abc.abstractproperty       # pragma: nocover
    def meta(self):
        """The resource's metadata as a :class:`kube.ObjectMeta` instance."""

    @abc.abstractmethod       # pragma: nocover
    def spec(self):
        """The spec of this node's resource.

        This returns a copy of the raw, decodeed JSON data
        representing the spec of this resource which can be used to
        re-create the resource.
        """

    @abc.abstractmethod       # pragma: nocover
    def watch(self):
        """Watch the resource for changes.

        Whenever the resource changes a new :class:`kube.WatchEvent`
        is returned.

        :returns: an iterator of :class:`kube.WatchEvent` instances
           for the resource.
        """


class Kind(enum.Enum):
    """The kinds of Kubernetes resources."""
    Node = 'Node'
    NodeList = 'NodeList'
    Namespace = 'Namespace'
    NamespaceList = 'NamespaceList'
    Pod = 'Pod'
    PodList = 'PodList'
    ReplicaSet = 'ReplicaSet'
    ReplicaSetList = 'ReplicaSetList'
    Service = 'Service'
    ServiceList = 'ServiceList'
    Secret = 'Secret'
    SecretList = 'SecretList'
