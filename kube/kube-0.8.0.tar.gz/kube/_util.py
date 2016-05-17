"""Common utilities kube."""

import collections
import datetime
import functools
import json

import pyrsistent

from kube import _error
from kube import _watch


def parse_rfc3339(when):
    """Parse a RFC 3339 timestamp into a :class:`datetime.datetime`."""
    return datetime.datetime.strptime(when, '%Y-%m-%dT%H:%M:%SZ')


def fetch_resource(cluster, resource, name, namespace=None):
    """Return the single resource data.

    This method helps implement common functionality for the
    :meth:`kube.ViewABC.fetch` method.  In particular it handles 404 as
    aa :class:`LookupError`.

    .. warning::

       Take care not to use this without a namespace when the resource
       does not support this, as this will result in a
       :class:`KeyError` instead of :class:`kube.APIError`.

    :returns: The decoded JSON object of the resource.
    :raises LookupError: if the resource does not exist.
    :raises kube.APIError: for errors from the k8s API server.
    """
    try:
        if namespace:
            data = cluster.proxy.get('namespaces', namespace, resource, name)
        else:
            data = cluster.proxy.get(resource, name)
    except _error.APIError as exc:
        if exc.status_code == 404:
            raise LookupError('No such resource: {}'.format(resource))
        else:
            raise
    else:
        return data


def filter_list(cluster, resource, labels, fields, namespace=None):
    """Return an iterator for a resource restricted to the selector.

    This method helps implement common functionality for the
    :meth:`kube.ViewABC.filter` method.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster
    :param resource: The resource name, defining the API server
       endpoint to use.
    :type resource: str
    :param labels: A label selector expression.  This can either
       be a dictionary with labels which must match exactly, or a
       string label expression as understood by k8s itself.
    :type labels: dict or str
    :param fields: A field selector expression.  This can either
       be a dictionary with fields which must match exactly, or a
       string field selector as understood by k8s itself.
    :type fields: dict or str
    :param namespace: Only include items in the given namespace.
    :type namespace: str

    :returns: an iterator of decoded JSON objects of resources
       matching the selector.
    :rtype: generator

    :raises ValueError: if an empty selector is used.
    :raises kube.APIError: for errors from the k8s API server.
    """
    if isinstance(labels, collections.abc.Mapping):
        if len(labels) == 0:
            raise ValueError('Empty labels selector')
        labels = ','.join('{}={}'.format(k, v) for k, v in labels.items())
    if isinstance(fields, collections.abc.Mapping):
        if len(fields) == 0:
            raise ValueError('Empty field selector')
        fields = ','.join('{}={}'.format(k, v) for k, v in fields.items())
    params = {}
    if labels:
        params['labelSelector'] = labels
    if fields:
        params['fieldSelector'] = fields
    if namespace:
        data = cluster.proxy.get('namespaces', namespace, resource, **params)
    else:
        data = cluster.proxy.get(resource, **params)
    yield from data['items']


def watch_item(item):
    """Watch a resource item for changes.

    Only changes after the current version will be part of the
    iterator.  However it can not be guaranteed that *every* change is
    returned, if the current version is rather old some changes might
    no longer be available.

    :param item: The Resource Item to watch.
    :type item: kube.ItemABC

    :returns: An iterator of the :class:`kube.WatchEvent` instances
       where the :attr:`kube.WatchEvent.item` attribute will be an
       instance of the class of the ``item`` param.

    :raises kube.APIError: For errors from the k8s API server.
    """
    fieldsel = {'metadata.uid': item.meta.uid}
    listurl = '/'.join(item.meta.link.split('/')[:-1])
    jsonwatcher = item.cluster.proxy.watch(listurl, fields=fieldsel)
    jsonwatcher.skip(item.meta.version)
    return _watch.ResourceWatcher(item.cluster, jsonwatcher, item.__class__)


def freeze(obj):
    """Freeze an object.

    This tries to make an object consisting of dicts, lists and
    primitive types immutable using pyrsistent.
    """
    return pyrsistent.freeze(obj)


def thaw(obj):
    """Thaw an objct.

    The reverse of :func:`freeze`.
    """
    return pyrsistent.thaw(obj)


def statusproperty(func):
    """Easily create properties for k8s status items.

    This turns the function into a property and will catch any
    exceptions, wrapping them into a :class:`kube.StatusError`.  This
    is far from perfect as it could easily be masking real bugs as
    well, the :attr:`StatusError.__cause__` attribute can still be
    used to find the original exception.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # pylint: disable=missing-docstring
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise _error.StatusError from err
    return property(wrapper)


class ImmutableJSONDecoder(json.JSONDecoder):
    """Decode JSON to immutable types."""

    def decode(self, string, *args, **kwargs):
        return freeze(super().decode(string, *args, **kwargs))
