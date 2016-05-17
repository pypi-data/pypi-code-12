"""Interface for pod resources."""

import enum
import ipaddress

import pyrsistent

from kube import _base
from kube import _error
from kube import _meta
from kube import _util
from kube import _watch


class PodView(_base.ViewABC):
    """View of the Pod resource items in the cluster.

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
            data = self.cluster.proxy.get('namespaces', self.namespace, 'pods')
        else:
            data = self.cluster.proxy.get('pods')
        for item in data['items']:
            yield PodItem(self.cluster, item)

    @property
    def kind(self):
        """The Kubernetes resource kind of the resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.PodList

    def fetch(self, name, namespace=None):
        """Retrieve an individual pod by name.

        This returns the current verison of the resource item.

        If the view itself is associated with a namespace, the
        :attr:`namespace` attribute is not ``None``, then this will
        default to fetching the pod resource item from this namespace.
        Otherwise the ``namespace`` parameter must be supplied.

        :param name: The name of the pod to retrive.
        :type name: str
        :param namespace: Use a namespace different from
           :attr:`namespace`.
        :type namespace: str

        :returns: A :class:`kube.PodItem` instance.

        :raises LookupError: If the pod does not exist.
        :raises NamespaceError: When no namespace was supplied.
        :raises kube.APIError: For errors from the k8s API server.
        """
        ns = namespace or self.namespace
        if not ns:
            raise _error.NamespaceError('Missing namespace')
        data = _util.fetch_resource(self.cluster, 'pods', name, namespace=ns)
        return PodItem(self.cluster, data)

    def filter(self, *, labels=None, fields=None):
        """Get a filtered iterator of pods.

        :param labels: A label selector expression.  This can either
           be a dictionary with labels which must match exactly, or a
           string label expression as understood by k8s itself.
        :type labels: dict or str
        :param fields: A field selector expression.  This can either
           be a dictionary with fields which must match exactly, or a
           string field selector as understood by k8s itself.
        :type fields: dict or str

        :returns: an iterator of :class:`Pod`s that match the given selector.
        :raises ValueError: If an empty selector is used.  An empty
           selector is almost certainly not what you want.  Kubernetes
           treats an **empty** selector as *all* items and treats a
           **null** selector as *no* items.
        :raises kube.APIError: for errors from the k8s API server.
        """
        data_iter = _util.filter_list(self.cluster, 'pods',
                                      labels=labels, fields=fields,
                                      namespace=self.namespace)
        for item in data_iter:
            yield PodItem(self.cluster, item)

    def watch(self):
        """Watch the PodList of this view for changes to items.

        Whenever one of the resource items in the view changes a new
        :class:`kube.WatchEvent` instance is yielded.  You can
        currently not control from "when" resources are being watched,
        other then from "now".  So be aware of any race conditions
        with watching.

        :returns: An iterator of :class:`kube.WatchEvent` instances
            where the :attr:`kube.WatchEvent.object` attribute will be
            a :class:`PodItem` instance.

        :raises kube.NamespaceError: When the namespace no longer
           exists.
        :raises kube.APIError: For errors from the k8s API server.
        """
        if self.namespace:
            path = ['namespaces', self.namespace, 'pods']
        else:
            path = ['pods']
        podlist = self.cluster.proxy.get(*path)
        version = podlist['metadata']['resourceVersion']
        jsonwatcher = self.cluster.proxy.watch(*path, version=version)
        return _watch.ResourceWatcher(self.cluster, jsonwatcher, PodItem)


class PodPhase(enum.Enum):
    """Enumeration of all possible pod phases.

    This is aliased to :attr:`Pod.PodPhase` for convenience.
    """
    Pending = 'Pending'
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'
    Unknown = 'Unknown'


class PodItem(_base.ItemABC):
    """A pod in the Kubernetes cluster.

    Each pod contains a number of containers and volumes which are executed
    on a node within the cluster. A pod may exist in a namespace. Pods are
    typically managed by a controller such as a replication controller or
    job.

    :param cluster: The cluster this pod exists in.
    :type cluster: kube.Cluster
    :param raw: The raw data of the resource item.
    :type raw: pyrsistent.PMap

    :cvar PodPhase: Convenience alias of :class:`PodPhase`.

    :ivar cluster: The :class:`kube.Cluster` this pod exists in.
    :ivar raw: The raw decoded JSON object as returned by the API
       server.  This is a :class:`pyrsistent.PMap` instance.
    """
    PodPhase = PodPhase

    def __init__(self, cluster, raw):  # pylint: disable=super-init-not-called
        self.cluster = cluster
        self.raw = raw

    @property
    def kind(self):
        """The Kubernetes resource kind of this resource.

        This is a :class:`kube.Kind` enum.
        """
        return _base.Kind.Pod

    @property
    def meta(self):
        """Pod's metadata as a :class:`kube.ObjectMeta`."""
        return _meta.ObjectMeta(self)

    def spec(self):
        """The spec of this pod's resource item.

        This a copy of the raw, decoded JSON data representing the
        spec of this pod.
        """
        return pyrsistent.thaw(self.raw['spec'])

    @_util.statusproperty
    def phase(self):
        """Phase of the pod as a :class:`kube.PodPhase`.

        :raises kube.StatusError: If this status item is not present.
        """
        return PodPhase(self.raw['status']['phase'])

    @_util.statusproperty
    def start_time(self):
        """Start the pod was started as a :class:`datetime.datetime`.

        :raises kube.StatusError: If this status item is not present.
        """
        return _util.parse_rfc3339(self.raw['status']['startTime'])

    @_util.statusproperty
    def ip(self):               # pylint: disable=invalid-name
        """IP address of the pod within the cluster.

        This may be as a :class:`ipaddress.IPv4Address` or a
        :class:`ipaddress.IPV6Address`.

        :raises kube.StatusError: If this status item is not present.
        """
        return ipaddress.ip_address(self.raw['status']['podIP'])

    @_util.statusproperty
    def host_ip(self):
        """IP address of the pod's host within the cluster.

        This  may be as a :class:`ipaddress.IPv4Address` or a
        :class:`ipaddress.IPv6Address`.

        :raises kube.StatusError: If this status item is not present.
        """
        return ipaddress.ip_address(self.raw['status']['hostIP'])

    @_util.statusproperty
    def message(self):
        """Human readable message explaining the pod's state.

        :raises kube.StatusError: If this status item is not present.
        """
        return self.raw['status']['message']

    @_util.statusproperty
    def reason(self):
        """PascalCase string explaining the pod's state.

        :raises kube.StatusError: If this status item is not present.
        """
        return self.raw['status']['reason']

    @property
    def containers(self):
        """Iterate over all :class:`Container`s in the pod."""
        statuses = self.raw['status'].get('containerStatuses', [])
        for container_status in statuses:
            yield Container(self, container_status)

    def watch(self):
        """Watch the pod for changes.

        Only changes after the current version will be part of the
        iterator.  However it can not be guaranteed that *every*
        change is returned, if the current version is rather old some
        changes might no longer be available.

        :returns: An iterator of :class:`kube.WatchEvent` instances
           where the :attr:`kube.WatchEvent.item` attribute will be
           a :class:`kube.PodItem` instance.

        :raises kube.APIError: For errors from the k8s API server.
        """
        return _util.watch_item(self)


class Container:
    """A container inside a pod.

    Containers live inside a pod and may be restarted inside this pod
    as controlled by the restart policy set on the pod.

    :param pod: The pod the container is part off.
    :type pod: PodItem
    :param raw: The JSON-decoded object describing the status of the
       container.
    :type raw: pyrsistent.PMap

    :ivar pod: The :class:`PodItem` instance the container is bound to.
    :ivar raw: The raw JSON-decoded object representing the container.
    """

    def __init__(self, pod, raw):
        self.pod = pod
        self.raw = raw

    def __repr__(self):
        return "<{0.__class__.__name__} {0.name!r} of {0.pod}>".format(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.raw == other.raw
        else:
            return NotImplemented

    @property
    def name(self):
        """The name of the container as a string."""
        return self.raw['name']

    @_util.statusproperty
    def state(self):
        """Current state of the container.

        This is represented by a :class:`ContainerState` instance.

        :raises kube.StatusError: If this status item is not present.
        """
        state = ContainerState(self.raw['state'])
        return state

    @_util.statusproperty
    def last_state(self):
        """Previous state of the container, if known.

        This is represented by a :class:`ContainerState` instance.

        :raises kube.StatusError: If this status item is not present.
        """
        if 'lastState' in self.raw and self.raw['lastState']:
            return ContainerState(self.raw['lastState'])
        else:
            raise _error.StatusError('No previous container state available')

    @_util.statusproperty
    def ready(self):
        """Boolean indicating if the container passed it's readyness probe.

        :raises kube.StatusError: If this status item is not present.
        """
        return bool(self.raw['ready'])

    @_util.statusproperty
    def restart_count(self):
        """The number of times the container was restarted as an integer.

        Note that this is currently not always accurate, it counts the
        number of dead containers which have not yet been removed.
        This means the gargage collection of containers caps this
        number at 5.
        """
        return int(self.raw['restartCount'])

    @_util.statusproperty
    def image(self):
        """The image the container is running.

        For Docker this is normally the repository name with tag
        appended.
        """
        return self.raw['image']

    @_util.statusproperty
    def image_id(self):
        """The ImageID of the container's image.

        For Docker this is in the ``docker://<hex_id>`` format.
        """
        return self.raw['imageID']

    @property
    def id(self):               # pylint: disable=invalid-name
        """The ID of the running container.

        For Docker this is in the ``docker://<hex_id>`` format.
        """
        return self.raw['containerID']


class ContainerState:
    """The state of a container within a pod.

    A container can be in one of three states: *running*, *waiting* or
    *terminated*.  This class provides a uniform interface to all
    states and their associated details.  Not all fields are always
    valid for each state so they can all raise an
    :exc:`kube.StatusError` when they are not available or not
    applicable.

    The overall state of the container is available both as a string
    in the :attr:`state` attribute as well as booleans in the
    :attr:`waiting`, :attr:`running` and :attr:`terminated`
    attributes.

    :param raw: The raw JSON-decoded ``v1.ContainerState`` API object
        as exposed by ``v1.ContainerStatus`` objects.
    :type raw: pyrsistent.PMap

    :ivar raw: The raw JSON-decoded object representing the container state.
    """

    def __init__(self, raw):
        # Sometimes k8s gets it wrong and ends up with multiple states
        # instead of just the one.  In this case the state in
        # lastState will still be present in the existing state.  So
        # we prefer states in a certain order.
        states = set(raw.keys())
        if len(states) > 1:
            if states == {'waiting', 'terminated'}:
                self._state = 'waiting'
            elif states == {'waiting', 'running'}:
                self._state = 'running'
            elif states == {'running', 'terminated'}:
                self._state = 'terminated'
            else:
                raise ValueError('Unknown state combination')
        else:
            self._state = states.pop()
        self._data = raw[self._state]
        self.raw = raw

    def __repr__(self):
        return '<{0.__class__.__name__} {0._state}>'.format(self)

    @property
    def waiting(self):
        """Boolean indicating if the container is waiting."""
        return self._state == 'waiting'

    @property
    def running(self):
        """Boolean indicating if the container is running."""
        return self._state == 'running'

    @property
    def terminated(self):
        """Boolean indicating if the container has been terminated."""
        return self._state == 'terminated'

    @_util.statusproperty
    def reason(self):
        """Brief reason explaining the container's state (str).

        This is normally a CamelCased message ID.

        Available for *waiting* and *terminated* states.

        :raises kube.StatusError: When this is not provided.
        """
        return self._data['reason']

    @_util.statusproperty
    def message(self):
        """Message regarding the container's state (str).

        Available for *waiting* and *terminated* states.

        :raises kube.StatusError: When this is not provided.
        """
        return self._data['message']

    @_util.statusproperty
    def started_at(self):
        """The time the container was started or restarted (datetime.datetime).

        Available for the *running* state.

        :raises kube.StatusError: When this is not provided.
        """
        return _util.parse_rfc3339(self._data['startedAt'])

    @_util.statusproperty
    def exit_code(self):
        """Exit code of the container (int).

        Available for the *terminated* state.

        :raises kube.StatusError: When this is not provided.
        """
        return self._data['exitCode']

    @_util.statusproperty
    def signal(self):
        """Last signal sent to the container, if known (int).

        Not all terminated containers can be expected to have this.

        .. warning::
            The signal is identified numerically, however these signal
            numbers are not portable therefore it's ill-advised to attempt
            to compare this value with the constants provided by the
            built-in :mod:`singal` module.

        Available for the *terminated* state.

        :raises kube.StatusError: When this is not provided.
        """
        return self._data['signal']

    @_util.statusproperty
    def finished_at(self):
        """The time the container was terminated (datetime.datetime).

        Available for the *terminated* state.

        :raises kube.StatusError: When this is not provided.
        """
        return _util.parse_rfc3339(self._data['finishedAt'])

    @_util.statusproperty
    def container_id(self):
        """The container ID of the terminated container.
        Available for the *terminated* state.

        :raises kube.StatusError: When this is not provided.
        """
        return self._data['containerID']
