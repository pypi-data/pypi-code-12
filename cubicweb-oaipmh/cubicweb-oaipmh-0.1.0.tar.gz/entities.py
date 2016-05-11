# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref entity's classes for OAI-PMH protocol"""
# TODO:  build the rql using syntax tree rather than string concatenation
# (using rqlquery?)


from abc import ABCMeta, abstractmethod

import rql
from cubicweb.view import EntityAdapter
from cubicweb.web.component import Component

from cubes.oaipmh import isodate


def parse_setspec(setspec):
    """Split a setpec string and return <etype>, <relation>, <value> parts."""
    if not setspec:
        raise ValueError('empty setspec')
    parts = setspec.split(':', 2)
    if len(parts) == 3:
        # setspec = etype:relation:value
        return parts
    elif len(parts) == 1:
        # setspec = etype
        return parts[0], None, None
    else:
        raise ValueError('only handling one or three levels set specifiers')


def build_setspec(*specitems):
    """Build a setspec from individual specifier items."""
    return ':'.join(specitems)


class OAIComponent(Component):
    """OAI-PMH protocol component handling set specifiers listing and querying.
    """
    __regid__ = 'oai'
    # maximum number of items for request returning a list of discrete items
    max_result_size = 20
    __setspecs__ = {}

    @classmethod
    def register(cls, specifier):
        """Register a top-level set specifier."""
        cls.__setspecs__[specifier.setkey] = specifier

    def setspecs(self):
        """Yield known set specifier string values"""
        for specifier in self.__setspecs__.itervalues():
            for setkey, description in specifier.setspecs(self._cw):
                yield setkey, description
                for subkey, child in specifier.iteritems():
                    for value, description in child.setspecs(self._cw):
                        if value is not None:
                            yield build_setspec(setkey, subkey, value), description

    def match_setspec(self, setspec, from_date=None, until_date=None,
                      token=None):
        """Return a ResultSet or None and a new token value.

        A result set is returned if `setspec` set specifier matches any of the
        adapter `setspecs`; else it is None. This result set has a size lower
        that class `max_result_size` attribute.

        A new token value is returned (in case a result set is returned, None
        otherwise) if there are more results to fetch from the same query.
        """
        etype, relation, value = parse_setspec(setspec)
        try:
            root = setspec = self.__setspecs__[etype]
        except KeyError:
            raise ValueError('no setspec matching {0}'.format(etype))
        if relation:
            try:
                setspec = root[relation]
            except KeyError:
                raise ValueError('unregistered setspec {0}'.format(setspec))
        setspec_where, args = setspec.setspec_restrictions(value)
        restrictions = [setspec_where]
        # Add dates restrictions.
        if from_date is not None:
            restrictions.append('X {0} >= %(from_date)s'.format(root.date_attr))
            args['from_date'] = from_date
        if until_date is not None:
            restrictions.append('X {0} <= %(until_date)s'.format(root.date_attr))
            args['until_date'] = until_date
        # Add token restriction.
        if token is not None:
            restrictions.append('X eid >= %(offset)s')
            args['offset'] = int(token)
        # Final query.
        qs = ('Any X ORDERBY X LIMIT {0} WHERE '.format(self.max_result_size + 1) +
              ', '.join(restrictions))
        rset = self._cw.execute(qs, args)
        return self.limit_rset(rset)

    def limit_rset(self, rset):
        """Return a result set limited to `max_result_size` along with a token.

        New token is the eid of the last entity in the result set (which is
        not included in the returned result set).
        """
        if len(rset) > self.max_result_size:
            token = str(rset[-1][0])
            rset = rset.limit(self.max_result_size, inplace=True)
        else:
            token = None
        return rset, token

    def match_identifier(self, identifier):
        """Return a result set matching identifier."""
        results = []
        for spec in self.__setspecs__.itervalues():
            qs, args = spec.query_for_identifier(unicode(identifier))
            try:
                rset = self._cw.execute(qs, args)
            except rql.TypeResolverException:
                # Probably no matching entity of target type with specified
                # identifier (may occur if several adapters share the same
                # identifier type, e.g. eid).
                continue
            if rset:
                assert not results, \
                    'ambiguous result for identifier {0}'.format(identifier)
                results.append(rset)
        return results[0] if results else self._cw.empty_rset()


class OAIPMHRecordAdapter(EntityAdapter):
    """Entity adapter representing an OAI-PMH record.

    Concret adapter are implemented for one entity type and define a top-level
    specifier to be returned by `set_definition` method.
    """
    __regid__ = 'IOAIPMHRecord'
    __abstract__ = True
    # the name of the attribute to be used as OAI identifier
    identifier_attribute = 'eid'
    # view identifier to generate metadata of OAI-PMH record
    metadata_view = None
    # date attribute to filter results by from/until request parameters
    date_attr = 'modification_date'
    # indicate that the record got deleted
    deleted = False

    @classmethod
    def __registered__(cls, *args):
        specifier = cls.set_definition()
        if specifier is not None:
            OAIComponent.register(specifier)
        return super(OAIPMHRecordAdapter, cls).__registered__(*args)

    @classmethod
    def set_definition(cls):
        """Return the top-level set specifier for adapter entity type.

        May return None if the adapter should not be registered within
        `OAIComponent`, e.g., if it is only used to build a record from an
        entity queried by its identifier not by a setspec.
        """
        return None

    @property
    def identifier(self):
        """OAI-PMH identifier for adapted entity."""
        return unicode(getattr(self.entity, self.identifier_attribute))

    @property
    def date(self):
        """OAI-PMH date information for adapted entity."""
        return getattr(self.entity, self.date_attr)

    @property
    def datestamp(self):
        """String representation of OAI-PMH date information for adapted entity.
        """
        return isodate(self.date)

    def metadata(self):
        """Return an XML-formatted representation of adapted entity."""
        if self.metadata_view is None:
            raise NotImplementedError(
                'undefined metadata_view attribute for {0}'.format(self.__class__))
        data = self._cw.view(self.metadata_view, w=None,
                             rset=self.entity.as_rset())
        if isinstance(data, unicode):
            # Underlying view may be 'binary' or not.
            data = data.encode('utf-8')
        return data


class OAISetSpec(object):
    """Base class for an OAI-PMH request set specifier."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def setspecs(self, cnx):
        """Yield setspec strings associated with this entry in the the setspec
        hierarchy.
        """

    @abstractmethod
    def setspec_restrictions(self, value=None):
        """Return the WHERE part of the RQL query string and a dict of query
        parameters for this set specifier.
        """


class ETypeOAISetSpec(OAISetSpec, dict):
    """OAI-PMH set specifier matching an entity type."""

    def __init__(self, etype, identifier_attribute, setkey=None,
                 date_attr=OAIPMHRecordAdapter.date_attr):
        """Build a top-level set specifier."""
        super(ETypeOAISetSpec, self).__init__()
        if setkey is None:
            setkey = etype.lower()
        self.etype = etype
        self.identifier_attribute = identifier_attribute
        self.setkey = setkey
        self.date_attr = date_attr

    def __setitem__(self, subset, specifier):
        """Register a new `OAISetSpec` as child of this object."""
        super(ETypeOAISetSpec, self).__setitem__(subset, specifier)
        specifier.__parent__ = self

    def setspecs(self, cnx):
        yield self.setkey, cnx._(self.etype)

    def setspec_restrictions(self, value=None):
        if value is not None:
            raise ValueError('unexpected setspec')
        return 'X is ' + self.etype, {}

    def query_for_identifier(self, identifier):
        """Return an RQL query string and a dict of query parameter for given
        `identifier` within the context of this set specifier.
        """
        if self.identifier_attribute == 'eid':
            try:
                identifier = int(identifier)  # XXX
            except ValueError:
                pass
        qs = 'Any X WHERE X is {etype}, X {attr} %(identifier)s'.format(
            etype=self.etype, attr=self.identifier_attribute)
        return qs, {'identifier': identifier}


class RelatedEntityOAISetSpec(OAISetSpec):
    """OAI-PMH second-level set specifier to match on a relation on the
    top-level entry.
    """

    def __init__(self, rtype, targettype, targetattr,
                 description=None, exclude=()):
        self.rtype = rtype
        self.targettype = targettype
        self.targetattr = targetattr
        self.description = description
        self.exclude = exclude
        self.__parent__ = None

    def setspecs(self, cnx):
        qs = 'DISTINCT String N WHERE X is {etype}, X {attr} N'
        if self.exclude:
            if len(self.exclude) > 1:
                qs += ', NOT X {{attr}} IN ({0})'.format(
                    ','.join(map(repr, self.exclude)))  # pylint: disable=bad-builtin
            else:
                qs += ', NOT X {{attr}} "{0}"'.format(
                    self.exclude[0])
        rset = cnx.execute(qs.format(
            etype=self.targettype, attr=self.targetattr))
        for value, in rset.rows:
            desc = self.description.format(value) if self.description else u''
            yield value, desc

    def setspec_restrictions(self, value):
        baseqs, args = self.__parent__.setspec_restrictions()
        subqs = 'X {rtype} Y, Y {attrname} %(value)s'.format(
            rtype=self.rtype, attrname=self.targetattr)
        qs = ', '.join([baseqs, subqs])
        args['value'] = unicode(value)
        return qs, args
