"""Interface for Secret resources."""

import base64
import enum

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


class SecretView(_base.ViewABC):
    """View of the Secret resource items in the cluster.

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
        """Iterate over all Secret resource items in the view.

        :returns: An object for each secret in the view.
        :rtype: kube.SecretItem

        :raises kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            data = self.cluster.proxy.get('namespaces',
                                          self.namespace, 'secrets')
        else:
            data = self.cluster.proxy.get('secrets')
        for item in data['items']:
            yield SecretItem(self.cluster, item)

    @property
    def kind(self):
        """The Kubernetes resource kind of the resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.SecretList

    def fetch(self, name, namespace=None):
        """Retrieve an individual secret by name.

        This returns the current verison of the resource item.

        If the view itself is associated with a namespace, the
        :attr:`namespace` attribute is not ``None``, then this will
        default to fetching the secret resource item from this
        namespace.  Otherwise the ``namespace`` parameter must be
        supplied.

        :param name: The name of the secret to retrive.
        :type name: str
        :param namespace: Use a namespace different from
           :attr:`namespace`.
        :type namespace: str

        :returns: A :class:`kube.SecretItem` instance.

        :raises LookupError: If the secret does not exist.
        :raises kube.NamespaceError: When no namespace was supplied.
        :raises kube.APIError: For errors from the k8s API server.
        """
        ns = namespace or self.namespace
        if not ns:
            raise _error.NamespaceError('Missing namespace')
        data = _util.fetch_resource(
            self.cluster, 'secrets', name, namespace=ns)
        return SecretItem(self.cluster, data)

    def filter(self, *, labels=None, fields=None):
        """Get a filtered iterator of secrets.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: an iterator of :class:`SecretItem`s that match the
           given selector.

        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: for errors from the k8s API server.
        """
        data_iter = _util.filter_list(self.cluster, 'secrets',
                                      labels=labels, fields=fields,
                                      namespace=self.namespace)
        for item in data_iter:
            yield SecretItem(self.cluster, item)

    def watch(self):
        """Watch the SecretList of this view for changes to items.

        Whenever one of the resource items in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances
            where the :attr:`kube.WatchEvent.object` attribute will be
            a :class:`SecretItem` instance.

        :raises kube.NamespaceError: When the namespace no longer
           exists.
        :raises kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            path = ['namespaces', self.namespace, 'secrets']
        else:
            path = ['secrets']
        svclist = self.cluster.proxy.get(*path)
        version = svclist['metadata']['resourceVersion']
        jsonwatcher = self.cluster.proxy.watch(*path, version=version)
        return _watch.ResourceWatcher(self.cluster, jsonwatcher, SecretItem)


class SecretType(enum.Enum):
    """Enumeration of secret types."""
    Opaque = 'Opaque'


class SecretItem(_base.ItemABC):
    """A Secret in the Kubernetes cluster.

    :param cluster: The cluster this Service exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :ivar cluster: The :class:`kube.Cluster` this Secret exists in.
    :ivar raw: The raw decoded JSON object as returned by the API
       server.  This is a :class:`pyrsistent.PMap` instance.
    """
    SecretType = SecretType

    def __init__(self, cluster, raw):  # pylint: disable=super-init-not-called
        self.cluster = cluster
        self.raw = raw

    @property
    def kind(self):
        """The Kubernetes resource kind of this resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.Secret

    @property
    def meta(self):
        """The Secret's metadata as a :class:`kube.ObjectMeta` instance."""
        return _meta.ObjectMeta(self)

    def spec(self):
        """An empty dictionary.

        This is supposed to be the secret resource item's spec.  But
        secrets do not have a spec, so to still follow the
        :class:`kube.ItemABC` we return an empty dict.
        """
        return {}

    def watch(self):
        """Watch the secret for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :returns: An iterator of :class:`kube.WatchEvent` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.SecretItem` instance.

        :raises kube.APIError: For errors from the k8s API server.
        """
        return _util.watch_item(self)

    @property
    def type(self):
        """The type of secret.

        There currently is only the "Opaque" type.
        """
        return self.SecretType(self.raw['type'])

    @property
    def data(self):
        """A mapping of the secret data.

        A copy of the secret data as a dict.  The keys are the names
        of the secrets as a (unicode) string, while the values are the
        secrets as bytestrings.

        Secret values are stored in a base64 encoding on the k8s
        master, but this is an implementation detail that this
        property takes care off for you.
        """
        data = {}
        for name, value in self.raw.get('data', {}).items():
            data[name] = base64.b64decode(value)
        return data
