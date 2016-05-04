# -*- coding: utf-8 -*-
"""
Sub-package containing the code that can read a DTD and return
a :class:`~dtd.root.DtdDefinition` object that
contains the nodes (elements, attributes, entities, etc.) extracted from this
DTD.

External programs should just call the
:func:`~dtd.read_dtd` method defined
at the top level of this package.

The other modules of this package contain all the classes and
functions necessary to read the DTD.

.. autofunction:: read_dtd
"""
__docformat__ = "restructuredtext en"


from .parser import DtdParser


def read_dtd(dtd_file, ns_mapping=None, qualify_local_elements=False,
              qualify_local_attributes=False):
    """
    Reads the ``xsd_dtd`` and returns a DtdDefinition object containing
    the nodes read in the DTD.

    The DTD doesn't support namespaces. The elements and attributes have to
    be declared with their prefix (e.g. ``xlink:href``). The ``ns_mapping``
    parameter allows the building of qualified names (namespace plus local
    name) from the DTD declatation.

    :param dtd_file:
        Name of the file that contains the DTD.
    :type dtd_file:
        :class:`unicode`
    :param ns_mapping:
        Mapping of prefixes towards namespaces ``{prefix: namespace}``. It is
        possible to give a default namespace by associating a namespace with
        ``u""`` or ``None``.
    :type ns_mapping:
        dict {:class:`unicode`: :class:`unicode`}
    :param qualify_local_elements:
        Flag indicating that the elements without a prefix must be qualified
        with the default namespace given in ``ns_mapping`` (namespace
        indexed with ``u""``).
    :type qualify_local_elements:
        :class:`bool`
    :param qualify_local_attributes:
        Flag indicating that the attributes without a prefix must be qualified
        with the default namespace given in ``ns_mapping`` (namespace
        indexed with ``u""``).
    :type qualify_local_attributes:
        :class:`bool`
    :returns:
        A DtdDefinition object grouping all the nodes read in the DTD.
    :rtype:
        :class:`~dtd.root.DtdDefinition`
    """
    prs = DtdParser(ns_mapping)
    prs.parse_dtd(dtd_file, qualify_local_elements, qualify_local_attributes)
    return prs.dtd_def
