"""Interface for ReplicaSet resources.

These used to be called ReplicationController before.
"""

import pyrsistent

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


class ReplicaSetView(_base.ViewABC):
    """View of the ReplicaSet resource items in the cluster.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param namespace: Limit the view to resource items in this
       namespace.
    :type namespace: str

    :ivar kube.Cluster cluster: The cluster instance this view is part of.
    :ivar str namespace: The namespace this view is contrained to, if
       the view is not bound to a namespace this will be ``None``.
    """

    def __init__(self, cluster, namespace=None):  # pylint: disable=super-init-not-called
        self.cluster = cluster
        self.namespace = namespace

    def __iter__(self):
        """Iterate over all Pod resource items in the view.

        :returns: An object for each pod in the view.
        :rtype: kube.PodItem

        :raises kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            data = self.cluster.proxy.get('namespaces', self.namespace,
                                          'replicationcontrollers')
        else:
            data = self.cluster.proxy.get('replicationcontrollers')
        for item in data['items']:
            yield ReplicaSetItem(self.cluster, item)

    @property
    def kind(self):
        """The Kubernetes resource kind of the resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.ReplicaSetList

    def fetch(self, name, namespace=None):
        """Retrieve an individual ReplicaSet by name.

        This returns the current verison of the resource item.

        If the view itself is associated with a namespace, the
        :attr:`namespace` attribute is not ``None``, then this will
        default to fetching the ReplicaSet resource item from this
        namespace.  Otherwise the ``namespace`` parameter must be
        supplied.

        :param name: The name of the ReplicaSet to retrive.
        :type name: str
        :param namespace: Use a namespace different from
           :attr:`namespace`.
        :type namespace: str

        :returns: A :class:`kube.ReplicaSetItem` instance.

        :raises LookupError: If the ReplicaSet does not exist.
        :raises NamespaceError: When no namespace was supplied.
        :raises kube.APIError: For errors from the k8s API server.
        """
        ns = namespace or self.namespace
        if not ns:
            raise _error.NamespaceError('Missing namespace')
        data = _util.fetch_resource(
            self.cluster, 'replicationcontrollers', name, namespace=ns)
        return ReplicaSetItem(self.cluster, data)

    def filter(self, *, labels=None, fields=None):
        """Get a filtered iterator of ReplicaSets.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: an iterator of :class:`ReplicaSet`s that match the
           given selector.

        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: for errors from the k8s API server.
        """
        data_iter = _util.filter_list(self.cluster, 'replicationcontrollers',
                                      labels=labels, fields=fields,
                                      namespace=self.namespace)
        for item in data_iter:
            yield ReplicaSetItem(self.cluster, item)

    def watch(self):
        """Watch the ReplicaSetList of this view for changes to items.

        Whenever one of the resource items in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances
            where the :attr:`kube.WatchEvent.object` attribute will be
            a :class:`ReplicaSetItem` instance.

        :raises kube.NamespaceError: When the namespace no longer
           exists.
        :raises kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            path = ['namespaces', self.namespace, 'replicationcontrollers']
        else:
            path = ['replicationcontrollers']
        rslist = self.cluster.proxy.get(*path)
        version = rslist['metadata']['resourceVersion']
        jsonwatcher = self.cluster.proxy.watch(*path, version=version)
        return _watch.ResourceWatcher(self.cluster,
                                      jsonwatcher, ReplicaSetItem)


class ReplicaSetItem(_base.ItemABC):
    """A ReplicaSet in the Kubernetes cluster.

    A ReplicaSet, formerly known as a ReplicationController, is
    responsible for keeping a desired number of pods running.

    :param cluster: The cluster this ReplicaSet exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :ivar cluster: The :class:`kube.Cluster` this ReplicaSet exists in.
    :ivar raw: The raw decoded JSON object as returned by the API
       server.  This is a :class:`pyrsistent.PMap` instance.
    """

    def __init__(self, cluster, raw):  # pylint: disable=super-init-not-called
        self.cluster = cluster
        self.raw = raw

    @property
    def kind(self):
        """The Kubernetes resource kind of this resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.ReplicaSet

    @property
    def meta(self):
        """The ReplicaSet's metadata as a :class:`kube.ObjectMeta` instance."""
        return _meta.ObjectMeta(self)

    def spec(self):
        """The spec of this ReplicaSet's resource item.

        This is a copy of the raw, decoded JSON data representing the
        spec of this ReplicaSet.
        """
        return pyrsistent.thaw(self.raw['spec'])

    def watch(self):
        """Watch the ReplicaSet for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :returns: An iterator of :class:`kube.WatchEvent` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.ReplicaSetItem` instance.

        :raises kube.APIError: For errors from the k8s API server.
        """
        return _util.watch_item(self)

    @_util.statusproperty
    def observed_replicas(self):
        """The current number of replicas observed."""
        return self.raw['status']['replicas']

    @_util.statusproperty
    def observed_generation(self):
        """The (integer) generation of the ReplicaSet."""
        return self.raw['status']['observedGeneration']

    @_util.statusproperty
    def fully_labeled_replicas(self):
        """Number of pods which have an exact matching set of labels.

        This counts the pods which have the exact same set of labels
        as the labelselector of this replicaset.
        """
        return self.raw['status']['fullyLabeledReplicas']
