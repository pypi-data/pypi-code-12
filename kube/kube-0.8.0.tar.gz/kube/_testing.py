"""Helpers for testing with the kube package.

This implements a :class:`StubAPIServerProxy` which you can program
yourself and does not require a real Kubernetes cluster to work.  The
idea is that it can be used as a drop-in replacement for the real
:class:`kube.APIServerProxy` for tests.

Currently this is not yet exposed as a public API but used in our own
tests.
"""

import binascii
import collections
import copy
import datetime
import hashlib
import os
import random
import time
import types
import urllib.parse
import uuid

import pyrsistent

from kube import _error


class StubResponse:
    """A fake requests.Response class for StubAPIError"""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self._message = message

    def json(self):
        """Return fake JSON data"""
        return {'status_code': self.status_code,
                'message': self._message if self._message else ''}


class StubAPIError(_error.APIError):
    """A kube.APIError subclass raisable without a response."""

    def __init__(self, status, message=None):  # pylint: disable=super-init-not-called
        response = StubResponse(status, message)
        super().__init__(response, message)


class StubAPIServerProxy:
    """An APIServerProxy which emulates a real k8s API server.

    The external API matches :class:`kube.APIServerProxy`, so for
    detailed docs see that class.
    """
    _Path = collections.namedtuple('Path', ['namespace', 'resource', 'name'])

    def __init__(self, base_url='http://localhost:8001/api/v1/', master=None):
        if not base_url.endswith('/'):
            base_url += '/'
        self._base_url = base_url
        if master is not None:
            self._master = master
        else:
            self._master = StubMaster()

    def close(self):
        """Close the underlying connections."""
        pass

    def urljoin(self, *path):
        """Wrapper around urllib.parse.urljoin for the configured base URL."""
        return urllib.parse.urljoin(self._base_url, '/'.join(path))

    def _parse_path(self, path):
        """Parse the path tuple.

        Returns a namedtuple of ``(namespace, resource, name)`` where
        both ``namespace`` and ``name`` can be *None* if they are not
        present in the path.
        """
        url = urllib.parse.urlsplit(self.urljoin(*path))
        items = url.path.split('/')
        base = urllib.parse.urlsplit(self._base_url).path.split('/')[:-1]
        items = items[len(base):]
        if len(items) > 2 and items[0] == 'namespaces':
            namespace = items[1]
            items = items[2:]
        else:
            namespace = None
        resource = items[0]
        try:
            name = items[1]
        except IndexError:
            name = None
        return self._Path(namespace, resource, name)

    def get(self, *path, **params):  # pylint: disable=unused-argument
        """HTTP GET the relative path from the API server."""
        namespace, resource_name, name = self._parse_path(path)
        try:
            resource = getattr(self._master, resource_name)
            if name is not None:
                data = resource.get(name, namespace=namespace)
            else:
                data = resource.select(namespace)
        except (KeyError, AttributeError):
            raise StubAPIError(404, 'No such resource item found')
        else:
            return pyrsistent.freeze(data)

    def post(self, *path, json=None, **params):  # pylint: disable=unused-argument
        """HTTP POST the relative path to the API server."""
        namespace, resource_name, _ = self._parse_path(path)
        try:
            resource = getattr(self._master, resource_name)
        except AttributeError:
            raise StubAPIError(404, 'No such resource item found')
        try:
            name = json['metadata']['name']
        except KeyError:
            basename = json['metadata']['generateName']
            name = basename + binascii.hexlify(os.urandom(3)).decode()
        rev = resource.revisions[-1]
        existing_names = {i['metadata']['name'] for i in rev.items}
        if name in existing_names:
            raise StubAPIError(409, 'Resource with name already exists')
        return pyrsistent.freeze(resource.create(namespace=namespace,
                                                 name=name,
                                                 data=json))

    def delete(self, *path, json=None, **params):  # pylint: disable=unused-argument,unused-variable
        """HTTP DELETE the relative path to the API server."""
        namespace, resource_name, item_name = self._parse_path(path)
        try:
            resource = getattr(self._master, resource_name)
        except AttributeError:
            raise StubAPIError(404, 'No such resource item found')
        resource.remove(item_name, namespace)

    def patch(self, *path, patch=None):
        """HTTP PATCH as application/strategic-merge-patch+json."""
        ppath = self._parse_path(path)
        try:
            resource = getattr(self._master, ppath.resource)
        except AttributeError:
            raise StubAPIError(404, 'No such resource item found')
        return resource.patch(ppath.name, patch, namespace=ppath.namespace)

    def watch(self, *path, version=None, fields=None):  # pylint: disable=unused-variable
        """Watch a list resource for events.

        Note that this ignores a named item in the resource as that is
        not really supported by k8s anyway.
        """
        path = self._parse_path(path)
        resource = getattr(self._master, path.resource)
        changes_iter = resource.watch(version)
        return StubJSONWatcher(resource, changes_iter)


class StubMaster:
    """A stub Kubernetes master server.

    This contains an API to manipulate the resources like the real k8s
    master API server does.
    """

    NAMESPACE_DATA = {
        'spec': {
            'finalizers': [
                'kubernetes',
            ],
        },
        'status': {
            'phase': 'Active',
        },
    }
    NODE_DATA = {
        'metadata': {           # Some of this is filled in automatically.
            'labels': {
                'kubernetes.io/hostname': 'kube-testnode-abc1',
            },
        },
        'spec': {
            'externalID': '17349516783711110824',
            'podCIDR': '10.120.0.0/24',
            'providerID': 'gce://project/europe-west1-d/kube-testnode-abc1',
        },
        'status': {
            'addresses': [
                {
                    'address': '10.240.0.2',
                    'type': 'InternalIP',
                },
                {
                    'address': '104.155.29.246',
                    'type': 'ExternalIP',
                }
            ],
            'capacity': {
                'cpu': '1',
                'memory': '1745136Ki',
                'pods': '40',
            },
            'conditions': [
                {
                    'lastHeartbeatTime': '2015-11-30T15:45:10Z',
                    'lastTransitionTime': '2015-11-07T20:25:16Z',
                    'reason': 'kubelet is posting ready status',
                    'status': 'True',
                    'type': 'Ready',
                }
            ],
            'nodeInfo': {
                'bootID': 'ecfa1657-c5f1-4388-b132-2bc5516cdb7c',
                'containerRuntimeVersion': 'docker://1.6.2',
                'kernelVersion': '3.16.0-0.bpo.4-amd64',
                'kubeProxyVersion': 'v1.0.6',
                'kubeletVersion': 'v1.0.6',
                'machineID': '',
                'osImage': 'Debian GNU/Linux 7 (wheezy)',
                'systemUUID': 'A3301D3F-154A-F537-9F39-34DF751661ED',
            },
        },
    }

    def __init__(self):
        self.nodes = StubResource('NodeList')
        self.nodes.create(namespace=None,
                          name='kube-testnode-abc1',
                          data=self.NODE_DATA)
        self.namespaces = StubResource('NamespaceList')
        self.namespaces.create(namespace=None,
                               name='default',
                               data=self.NAMESPACE_DATA)
        self.pods = StubResource('PodList', create_cb=self._create_pod)
        self._pod_count = 1
        self.replicationcontrollers = StubResource(
            'ReplicationControllerList', create_cb=self._create_replicaset)
        self.services = StubResource('ServiceList')
        self.secrets = StubResource('SecretList',
                                    create_cb=self._create_secret)

    def _create_pod(self, data):
        """Callback to customise creation of pod resource items."""
        data['status']['phase'] = 'Running'
        start_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        data['status']['startTime'] = start_time
        data['status']['podIP'] = '192.0.2.{}'.format(self._pod_count)
        self._pod_count += 1
        data['status']['hostIP'] = '192.51.100.1'
        base_hash = hashlib.sha256(data['metadata']['namespace'].encode())
        base_hash.update(data['metadata']['name'].encode())
        data['status']['containerStatuses'] = []
        for spec in data['spec']['containers']:
            c_hash = base_hash.copy()
            c_hash.update(spec['name'].encode())
            cid_hash = c_hash.copy()
            cid_hash.update(b'containerID')
            iid_hash = c_hash.copy()
            iid_hash.update(b'imageID')
            status = {
                'containerID': 'docker://{}'.format(cid_hash.hexdigest()),
                'name': spec['name'],
                'ready': True,
                'restartCount': 0,
                'image': spec['image'],
                'imageID': 'docker://{}'.format(iid_hash.hexdigest()),
                'state': {
                    'running': {
                        'startedAt': start_time,
                    },
                },
            }
            data['status']['containerStatuses'].append(status)
        return data

    @staticmethod
    def _create_replicaset(data):
        """Callback to customise creation of ReplicaSet resource items."""
        data['status']['replicas'] = data['spec']['replicas']
        data['status']['observedGeneration'] = 1
        data['status']['fullyLabeledReplicas'] = 1
        return data

    @staticmethod
    def _create_secret(data):
        """Callback to default to the Opaque secret type."""
        if 'type' not in data:
            data['type'] = 'Opaque'
        return data


class StubResource:
    """Represent a stubbed out resource.

    This contains the API which to manage a single k8s resource in a
    generic way.

    :param  kind: The resource kind, e.g. NodeList, PodList, etc.  Note
       that the base resource must always be a *List in k8s.
    :type kind: str
    :param create_cb: An optional callback which will be called when a
       new item is created.  It should take the dict of data and return
       the, optionally modified, same dict of data.
    :type create_cb: types.FunctionType
    """
    Revision = collections.namedtuple('Revision', ['rev', 'items'])
    Revision.__doc__ = """Represents a revision of a k8s resource list.

    Each revision has the integer ``rev`` number and the ``items`` as
    a :class:`pyrsistent.PSet` of :class:`pyrsistent.PMap` instance
    containing their raw data.
    """

    def __init__(self, kind, create_cb=None):
        self.kind = kind
        self._create_cb = create_cb
        self.name = kind[:-4].lower() + 's'
        self.api_version = 'v1'
        initial_rev = random.randint(1, 2000000)
        initial_items = pyrsistent.pset()
        self.revisions = collections.deque(
            [self.Revision(initial_rev, initial_items)], maxlen=200)

    def __repr__(self):
        return '<StubResource {0.kind}>'.format(self)

    def create(self, namespace, name, data):
        """Create a new resource item.

        This adds a new named item to the resource list.  This is
        fairly crude for now and does not match k8s creation semantics
        yet, just a way to get a new resource item.  Note that some
        info in the metadata should not be provided and will be filled
        in automatically:

        - apiVersion
        - kind
        - metadata.creationTimestamp
        - metadata.labels
        - metadata.name
        - metadata.resourceVersion
        - metadata.selfLink
        - metadata.uid

        If you do provide one of these items they will overwrite the
        default ones and you can risk creating an incorrect item,
        e.g. by having a mismatching name.

        :param namespace: The namespace this resource belongs too.
           Use ``"default"`` for the default namespace.  Use ``None``
           for resources which do not belong to namespaces like
           NodeList.
        :type namespace: str or None.
        :param name: The name of the item to create.
        :type name: str
        :param data: The raw data for the item.
        :type data: collections.abc.Mapping
        """
        last = self.revisions[-1]
        names = [i['metadata']['name'] for i in last.items
                 if i['metadata'].get('namespace') == namespace]
        if name in names:
            raise KeyError('Name already exists')
        rev = last.rev + 1
        selflink = '/api/{r.api_version}{ns}/{r.name}/{name}'.format(
            r=self,
            ns='/namespaces/{}'.format(namespace) if namespace else '',
            name=name,
        )
        default_meta = {
            'creationTimestamp':
                datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'labels': {},
            'name': name,
            'resourceVersion': str(rev),
            'selfLink': selflink,
            'uid': str(uuid.uuid4()),
        }
        new_item = copy.deepcopy(data)
        default_meta.update(new_item.get('metadata', {}))
        new_item['metadata'] = default_meta
        if 'spec' not in new_item:
            new_item['spec'] = {}
        if 'status' not in new_item:
            new_item['status'] = {}
        if 'kind' not in new_item:
            new_item['kind'] = self.kind.rstrip('List')
        if 'apiVersion' not in new_item:
            new_item['apiVersion'] = self.api_version
        if self._create_cb:
            new_item = self._create_cb(new_item)
        new_items = last.items.add(pyrsistent.freeze(new_item))
        self.revisions.append(self.Revision(rev, new_items))
        return new_item

    def get(self, name, namespace=None):
        """Retreive a named item from the resource.

        This will retrieve the latest version of the named resource in
        the given namespace.

        :param str name: The name of the item to retreive.
        :param str namespace: The namespace of the item to retrieve.

        :returns: The mapping describing the item.
        :rtype: pyrsistent.PMap

        :raises KeyError: When the item is not found.
        """
        last = self.revisions[-1]
        items = {i for i in last.items
                 if (i['metadata'].get('namespace') == namespace and
                     i['metadata']['name'] == name)}
        return items.pop()

    def remove(self, name, namespace=None):
        """Remove the named item."""
        last = self.revisions[-1]
        for item in last.items:
            if (item['metadata'].get('namespace') == namespace and
                    item['metadata']['name'] == name):
                break
        else:
            raise LookupError('No such item')
        new_items = last.items.remove(item)  # pylint: disable=undefined-loop-variable
        self.revisions.append(self.Revision(last.rev+1, new_items))

    def patch(self, name, patch, namespace=None):
        """Apply a strategic merge patch to the named item in the resource.

        This creates a new version of the resource with the named item
        modified from the changes specified by the patch.

        :param str name: The name of the resource item.
        :param dict patch: The patch as deserialised JSON.
        :param str namespace: The namespace of the resource item.

        :returns: The new item after the patch is applied.
        :rtype: pyrsistent.PMap
        """
        old = self.get(name, namespace)
        tmp = pyrsistent.thaw(old)
        self._patch(tmp, patch)
        last = self.revisions[-1]
        tmp['metadata']['resourceVersion'] = str(last.rev + 1)
        new = pyrsistent.freeze(tmp)
        items = last.items.remove(old).add(new)
        self.revisions.append(self.Revision(last.rev + 1, items))
        return new

    def _patch(self, obj, patch):
        """Patch a dict object.

        This can recusively apply the logic required to patch a dict.
        It is a JSON Merge Patch (:rfc:`7396`) and not the k8s
        strategic merge patch.

        :param obj: The object to patch.
        :type obj: dict, *must* be mutable.
        :param patch: The patch *for this object*, for a nested object
           this can be a subset of the patch just pertaining this
           object.
        :type patch: collections.abc.Mapping.
        """
        for key, value in patch.items():
            if value is None:
                try:
                    del obj[key]
                except KeyError:
                    pass
            elif isinstance(value, collections.abc.Mapping):
                self._patch(obj[key], patch[key])
            else:
                obj[key] = value

    def select(self, namespace=None):
        """Select multiple items from the resource.

        Currently can only select all or filter on namespace.

        :param str namespace: Restrict selected items to given
           namespace.
        """
        last = self.revisions[-1]
        if namespace is not None:
            items = pyrsistent.pset(
                i for i in last.items
                if i['metadata'].get('namespace') == namespace
            )
        else:
            items = last.items
        return pyrsistent.freeze({
            'apiVersion': self.api_version,
            'items': copy.deepcopy(items),
            'kind': self.kind,
            'metadata': {
                'resourceVersion': str(last.rev),
                'selfLink': '/api/{}/{}'.format(
                    self.api_version,
                    self.kind.rstrip('List').lower() + 's',
                ),
            },
        })

    def _nextrev(self, rev):
        """Return the next revision number for the resource.

        Use ``None`` to get the first revision number.
        """
        for resource in self.revisions:
            if rev is None or resource.rev > rev:
                return resource
        else:                   # pylint: disable=useless-else-on-loop
            raise LookupError

    def watch(self, version=None):
        """Return generator yielding changes for this resource.

        Note that this will raise StopIteration when there are no more
        changes.  To avoid pre-maturely terminating the generator use
        the :meth:`wait` method to find out if more data is available.

        :param int version: The optional version to start watching from.
        """
        if version is not None:
            version = int(version)
            last = self._nextrev(version - 1)
            curr = self._nextrev(version)
        else:
            last = self.revisions[0]
            curr = self.revisions[1]
        while True:
            yield self._compare_revisions(last, curr)
            last = curr
            try:
                curr = self._nextrev(last.rev)
            except LookupError:
                return

    @staticmethod
    def _compare_revisions(prev, curr):
        """Compare two revisions and generate change object.

        This generates the change object for :meth:`watch`.
        """
        if len(prev.items) < len(curr.items):
            new = curr.items - prev.items
            assert len(new) == 1
            return pyrsistent.pmap({
                'type': 'ADDED',
                'object': next(iter(new)),
            })
        elif len(prev.items) > len(curr.items):
            rem = prev.items - curr.items
            assert len(rem) == 1
            return pyrsistent.pmap({
                'type': 'DELETED',
                'object': next(iter(rem)),
            })
        else:
            prevd = {i['metadata']['uid']: i for i in prev.items}
            currd = {i['metadata']['uid']: i for i in curr.items}
            prev_uids = sorted(prevd.keys())
            curr_uids = sorted(currd.keys())
            assert prev_uids == curr_uids
            for uid, prev_item in prevd.items():
                if prev_item != currd[uid]:
                    return pyrsistent.pmap({
                        'type': 'MODIFIED',
                        'object': currd[uid],
                    })

    def wait(self, last_rev, timeout):
        """Wait for the next revision to be ready.

        :param int last_rev: The previous revision.  If ``None`` this
           will wait for the first revision.
        :param int timeout: The time to wait in seconds.

        :returns: ``True`` if the next revision is available,
           ``False`` if not.
        :rtype: bool
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() <= deadline:
            try:
                self._nextrev(last_rev)
            except LookupError:
                time.sleep(0.02)
            else:
                return True
        return False


class StubJSONWatcher:
    """A stub JSONWatcher instance to work with :class:`StubMaster`.

    This matches the :class:`kube._watch.JSONWatcher` class but
    works with the :class:`StubMaster` instead.  See the original
    class for full docstrings.

    Note that the constructor has a different signature as this is not
    part of the public API.  Also note that it does provide a (fake)
    ``._sock.fileno()`` method which will return -1 after
    :meth:`close` has been called, this is to support the tests.

    :param resource: The resource this instance is watching.
    :type resource: StubResource
    :param changes_iter: The generator from :meth:`StubResource.wait`.
    :type changes_iter: generator
    """

    def __init__(self, resource, changes_iter):
        self._resource = resource
        self._changes_iter = changes_iter
        self._last_rev = None
        self._sock = types.SimpleNamespace(fileno=self._stub_fileno)
        self._fake_fileno = 42

    def _stub_fileno(self):
        """Fake socket.fileno() function."""
        return self._fake_fileno

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self, *, timeout=None):
        """Return the next line."""
        if timeout is not None:
            ready = self._resource.wait(self._last_rev, timeout)
            if not ready:
                raise TimeoutError('No new revision available')
        item = next(self._changes_iter)
        return pyrsistent.thaw(item)

    def skip(self, version):
        """Skip past given version if possible."""
        pass

    def close(self):
        """Close the iterator."""
        self._fake_fileno = -1

    def __enter__(self):
        pass

    def __exit__(self, exc_val, exc_type, traceback):
        self.close()
