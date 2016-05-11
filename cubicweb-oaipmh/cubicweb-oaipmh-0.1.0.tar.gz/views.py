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
"""cubicweb-oaipmh views for OAI-PMH export

Set hierarchy specification
---------------------------

Sets_ are optional construct for selective harvesting. The scheme used to
define the syntax of sets is usually specific to the community using the
OAI-PMH exchange protocol. This OAI-PMH implementation exposes the following
set hierarchy.

- The first level of hierarchy refers to the entity type to perform the
  selective request on, e.g. for a `ListIdentifiers` verb:

      <baseurl>/oai?verb=ListIdentifiers&set=agent

  would return the identifiers of entities of type Agent found in the repository.

- The second level of hierarchy refers to a filtering criterion on selected
  entity type, usually an attribute with respect to the application schema,
  and is tight to a value of this criterion (attribute) to filter entities on.
  For instance:

      <baseurl>/oai?verb=ListIdentifiers&set=agent:kind:person

  would return the identifiers of entities of type Agent of kind 'person'.

.. _Set:
.. _Sets: http://www.openarchives.org/OAI/openarchivesprotocol.html#Set
"""

from datetime import datetime, timedelta

import dateutil.parser
from lxml import etree
from lxml.builder import E, ElementMaker
import pytz

from cubicweb.predicates import ExpectedValuePredicate, match_form_params
from cubicweb.view import View
from cubicweb.web.views import urlrewrite

from cubes.oaipmh import isodate


def utcparse(timestr):
    """Parse a date/time string as an UTC datetime *without* tzinfo."""
    date = dateutil.parser.parse(timestr)
    if date.tzinfo is None:
        if 'T' in timestr:
            raise ValueError('cannot parse a date with time but no timezone')
        else:
            # No time nor tzinfo: done.
            return date
    else:
        # Convert to UTC and drop tzinfo.
        return date.astimezone(pytz.utc).replace(tzinfo=None)


class match_verb(ExpectedValuePredicate):
    """Predicate checking `verb` request form parameter presence and value.

    Return 2 in case of match, for precedence over
    ``match_form_params('verb')``.
    """

    def __call__(self, cls, req, rset=None, **kwargs):
        verb = req.form.get('verb')
        if verb is None:
            return 0
        return 2 * int(verb in self.expected)


def filter_none(mapping):
    """Return a dict from `mapping` with None values filtered out."""
    out = {}
    for key, val in mapping.iteritems():
        if val is not None:
            out[key] = val
    return out


def oai_records(rset):
    """Yield OAIRecord items from a result set."""
    for entity in rset.entities():
        record = entity.cw_adapt_to('IOAIPMHRecord')
        if not record:
            continue
        yield OAIRecord(record)


class OAIError(Exception):
    """Error in OAI-PMH request."""

    def __init__(self, errors):
        super(OAIError, self).__init__()
        self.errors = errors


class OAIRequest(object):
    """Represent an OAI-PMH request."""

    @classmethod
    def from_request(cls, baseurl, request):
        form = request.form
        return cls(
            baseurl,
            setspec=form.get('set'),
            verb=form.get('verb'),
            identifier=form.get('identifier'),
            from_date=form.get('from'),
            until_date=form.get('until'),
            resumption_token=form.get('resumptionToken'),
        )

    def __init__(self, baseurl, verb=None, setspec=None, identifier=None,
                 from_date=None, until_date=None, resumption_token=None):
        self.baseurl = baseurl
        self.verb = verb
        self.setspec = setspec
        self.identifier = identifier
        self.errors = {}
        # Parse "from" and "until" dates, which are, by specification
        # expressed in UTC.
        if from_date is not None:
            from_date = utcparse(from_date)
        if until_date is not None:
            until_date = utcparse(until_date)
        if (from_date is not None and until_date is not None and
                from_date > until_date):
            msg = 'the from argument must be less than or equal to the until argument'
            self.errors['badArgument'] = msg
        self.from_date = from_date
        self.until_date = until_date
        self.resumption_token = resumption_token

    def __repr__(self):
        return etree.tostring(self.to_xml())

    def rset_from_identifier(self, cnx):
        """Return a ResultSet corresponding to request identifier."""
        oai = cnx.vreg['components'].select('oai', cnx)
        return oai.match_identifier(self.identifier)

    def rset_from_setspec(self, cnx):
        """Return a result set from OAI-PMH request set specifier, possibly
        with a resumptionToken information.
        """
        dates = {'from_date': self.from_date,
                 'until_date': self.until_date}
        oai = cnx.vreg['components'].select('oai', cnx)
        try:
            rset, token = oai.match_setspec(
                self.setspec, token=self.resumption_token, **dates)
        except ValueError:
            raise OAIError(
                {'noRecordsMatch': 'invalid set specifier {0}'.format(self.setspec)})
        if not rset:
            if self.resumption_token is not None:
                raise OAIError(
                    {'badResumptionToken': ('The value of the resumptionToken '
                                            'argument is invalid or expired.')})
            raise OAIError(
                {'noRecordsMatch': ('The combination of the values of the '
                                    'from, until, and set arguments results '
                                    'in an empty list.')})
        return rset, token

    def new_token(self, token):
        """Return a resumptionToken XML element or None.

        * return a resumptionToken with a value if there are more result to be
        fetched;
        * return an empty resumptionToken if this response completes and the
        request contains a resumptionToken;
        * None otherwise.
        """
        if token is not None:
            expire = isodate(datetime.now(pytz.utc) + timedelta(hours=1))
            return E.resumptionToken(token, expirationDate=expire)
        elif self.resumption_token is not None:
            return E.resumptionToken()

    def to_xml(self, errors=None):
        if not errors:
            # In cases where the request that generated this response resulted
            # in a badVerb or badArgument error condition, the repository must
            # return the base URL of the protocol request only. Attributes
            # must not be provided in these cases.
            attributes = {
                'verb': self.verb,
                'identifier': self.identifier,
                'set': self.setspec,
            }
            if self.from_date:
                attributes['from'] = isodate(self.from_date)
            if self.until_date:
                attributes['until'] = isodate(self.until_date)
        else:
            attributes = {}
        attributes = filter_none(attributes)
        return E.request(self.baseurl, **attributes)


class OAIResponse(object):
    """Represent an OAI-PMH response."""

    def __init__(self, oai_request):
        self.oai_request = oai_request

    @staticmethod
    def _build_errors(errors):
        """Return a list of <error> tag from `errors` dict."""
        return [E.error(msg, code=code)
                for code, msg in errors.iteritems()]

    def body(self, content=None, errors=None):
        """Return a list of body items of the OAI-PMH response."""
        oai_request = self.oai_request
        if errors:
            return self._build_errors(errors)
        assert content is not None, \
            'unexpected empty content while no error got reported'
        try:
            return [E(oai_request.verb, *content)]
        except OAIError as exc:
            return self._build_errors(exc.errors)

    def to_xml(self, content=None, errors=()):
        date = E.responseDate(isodate())
        request = self.oai_request.to_xml(errors)
        body_elems = self.body(content, errors=errors)
        nsmap = {None: 'http://www.openarchives.org/OAI/2.0/',
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        maker = ElementMaker(nsmap=nsmap)
        attributes = {
            '{%s}schemaLocation' % nsmap['xsi']: ' '.join([
                'http://www.openarchives.org/OAI/2.0/',
                'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'
            ])
        }
        return maker('OAI-PMH', date, request, *body_elems, **attributes)


class OAIRecord(object):
    """Represent an OAI record built from an entity adapted as IOAIPMHRecord.
    """

    def __init__(self, record):
        self.record = record

    def header(self):
        """The <header> part of an OAI-PMH record.

        See http://www.openarchives.org/OAI/openarchivesprotocol.html#header
        for a description of elements of a "header".
        """
        # TODO: add setSpec tag for each record.
        tags = []
        for tag in ('identifier', 'datestamp'):
            value = getattr(self.record, tag)
            if value:
                tags.append(E(tag, value))
        attrs = {}
        if self.record.deleted:
            attrs['status'] = 'deleted'
        return E.header(*tags, **attrs)

    def metadata(self):
        """The <metadata> part of an OAI-PMH record."""
        if self.record.deleted:
            return None
        metadata = self.record.metadata()
        if metadata:
            return E.metadata(etree.XML(metadata))
        return None

    def to_xml(self):
        """Return the <record> XML element."""
        elems = [self.header()]
        metadata = self.metadata()
        if metadata is not None:  # deleted record
            elems.append(metadata)
        return E.record(*elems)


class OAIPMHRewriter(urlrewrite.SimpleReqRewriter):
    rules = [('/oai', dict(vid='oai'))]


class OAIView(View):
    """Base class for any OAI view, subclasses should either implement
    `errors` or `verb_content` methods.
    """
    __regid__ = 'oai'
    __abstract__ = True
    templatable = False
    content_type = 'text/xml'
    binary = True

    @staticmethod
    def verb_content():
        return

    @staticmethod
    def errors():
        """Return the errors of the OAI-PMH request."""
        return {}

    def __init__(self, *args, **kwargs):
        super(OAIView, self).__init__(*args, **kwargs)
        self.oai_request = OAIRequest.from_request(
            self._cw.build_url('oai'), self._cw)

    def call(self):
        encoding = self._cw.encoding
        assert encoding == 'UTF-8', 'unexpected encoding {0}'.format(encoding)
        self.w('<?xml version="1.0" encoding="%s"?>\n' % encoding)
        oai_response = OAIResponse(self.oai_request)
        # combine errors coming from view selection with those of request
        # processing.
        errors = self.errors()
        errors.update(self.oai_request.errors)
        response_elem = oai_response.to_xml(self.verb_content(), errors=errors)
        self.w(etree.tostring(response_elem, encoding='utf-8'))


class OAIBaseView(OAIView):
    """Base view for OAI-PMH request with no "verb" specified.

    `verb` request parameter is necessary in our implementation.
    """

    def errors(self):
        return {'badVerb': 'no verb specified'}


class OAIWithVerbView(OAIView):
    """Base view for OAI-PMH request with a "verb" specified.

    This view generated an error as the implementation relies on explicit view
    to handle supported verbs.
    """
    __select__ = match_form_params('verb')

    def errors(self):
        """Return the errors of the OAI-PMH request."""
        return {'badVerb': 'illegal verb "{0}"'.format(self.oai_request.verb)}


class OAIListSetsView(OAIView):
    """View handling verb="ListSets" requests."""
    __select__ = match_verb('ListSets')

    @staticmethod
    def build_set(spec, name=u''):
        """Return a "set" element"""
        return E('set', E.setSpec(spec), E.setName(name))

    def verb_content(self):
        oai = self._cw.vreg['components'].select('oai', self._cw)
        for spec, description in oai.setspecs():
            yield self.build_set(spec, name=self._cw._(description))


class OAIListIdentifiersView(OAIView):
    """View handling verb="ListIdentifiers" requests.

    This view returns an error as it handles cases where no "set" selection is
    specified.
    """
    __select__ = match_verb('ListIdentifiers')

    def errors(self):
        return {
            'badArgument': 'ListIdentifiers verb requires "set" restriction'}


class OAIListIdentifiersWithSetView(OAIView):
    """View handling verb="ListIdentifiers" requests with "set" selection."""
    __select__ = match_form_params('set') & match_verb('ListIdentifiers')

    def verb_content(self):
        rset, token = self.oai_request.rset_from_setspec(self._cw)
        for record in oai_records(rset):
            yield record.header()
        new_token = self.oai_request.new_token(token)
        if new_token is not None:
            yield new_token


class OAIListRecordsView(OAIView):
    """View handling verb="ListRecords" requests.

    This view returns an error as it handles cases where no "set" selection is
    specified.
    """
    __select__ = match_verb('ListRecords')

    def errors(self):
        return {
            'badArgument': 'ListRecords verb requires "set" restriction'}


class OAIListRecordsWithSetView(OAIView):
    """View handling verb="ListRecords" requests with "set" selection."""
    __select__ = match_form_params('set') & match_verb('ListRecords')
    # TODO: handle metadataPrefix, which is a required argument of this verb.

    def verb_content(self):
        rset, token = self.oai_request.rset_from_setspec(self._cw)
        for record in oai_records(rset):
            yield record.to_xml()
        new_token = self.oai_request.new_token(token)
        if new_token is not None:
            yield new_token


class OAIGetRecordErrorView(OAIView):
    """View handling verb="GetRecord" requests with errors.

    This view returns an error as it handles cases where no "identifier" selection is
    specified.
    """
    __select__ = match_verb('GetRecord')

    def errors(self):
        return {'badArgument': ('GetRecord verb requires "identifier" and '
                                '"metadataPrefix" arguments')}


class OAIGetRecordView(OAIView):
    """View handling verb="GetRecord" with proper arguments."""
    __select__ = match_form_params('identifier') & match_verb('GetRecord')
    # TODO: handle metadataPrefix, which is a required argument of this verb.

    def verb_content(self):
        rset = self.oai_request.rset_from_identifier(self._cw)
        for record in oai_records(rset):
            if record is not None:
                yield record.to_xml()
                break
        else:
            msg = 'no entity with OAI identifier {0} in repository'.format(
                self.oai_request.identifier)
            raise OAIError({'idDoesNotExist': msg})
