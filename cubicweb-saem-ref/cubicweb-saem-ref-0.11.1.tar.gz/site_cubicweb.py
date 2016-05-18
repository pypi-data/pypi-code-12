# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref site customizations"""

import pytz

from logilab.common.date import ustrftime
from logilab.common.decorators import monkeypatch

from yams.constraints import OPERATORS, BoundaryConstraint, Attribute

from cubicweb import cwvreg
from cubicweb.cwconfig import register_persistent_options
from cubicweb.uilib import PRINTERS

from cubes.skos import rdfio
from cubes.skos.ccplugin import ImportSkosData

from cubes.saem_ref import cwuri_url
from cubes.saem_ref.sobjects.skos import SAEMMetadataGenerator
# this import is needed to take account of pg_trgm monkeypatches
# while executing cubicweb-ctl commands (db-rebuild-fti)
from cubes.saem_ref import pg_trgm  # noqa pylint: disable=unused-import

_ = unicode


@monkeypatch(rdfio.RDFGraphGenerator, methodname='equivalent_concept_uris')
@staticmethod
def equivalent_concept_uris(entity):
    yield cwuri_url(entity)


# deactivate date-format and datetime-format cw properties. This is because we do some advanced date
# manipulation such as allowing partial date and this is not generic enough to allow arbitrary
# setting of date and time formats

base_user_property_keys = cwvreg.CWRegistryStore.user_property_keys


@monkeypatch(cwvreg.CWRegistryStore)
def user_property_keys(self, withsitewide=False):
    props = base_user_property_keys(self, withsitewide)
    return [prop for prop in props if prop not in ('ui.date-format', 'ui.datetime-format')]

# customize display of TZDatetime

register_persistent_options((
    ('timezone',
     {'type': 'choice',
      'choices': pytz.common_timezones,
      'default': 'Europe/Paris',
      'help': _('timezone in which time should be displayed'),
      'group': 'ui', 'sitewide': True,
      }),
))


def print_tzdatetime_local(value, req, *args, **kwargs):
    tz = pytz.timezone(req.property_value('ui.timezone'))
    value = value.replace(tzinfo=pytz.utc).astimezone(tz)
    return ustrftime(value, req.property_value('ui.datetime-format'))

PRINTERS['TZDatetime'] = print_tzdatetime_local


# configure c-c skos-import command's factories to use with proper metadata generator ##############

def _massive_store_factory(cnx):
    from cubes.saem_ref.backports.massive_store import MassiveObjectStore
    return MassiveObjectStore(cnx, metagen=SAEMMetadataGenerator(cnx))


def _nohook_store_factory(cnx):
    from cubes.saem_ref.backports.stores import NoHooRQLObjectStore
    return NoHooRQLObjectStore(cnx, metagen=SAEMMetadataGenerator(cnx))


ImportSkosData.cw_store_factories['massive'] = _massive_store_factory
ImportSkosData.cw_store_factories['nohook'] = _nohook_store_factory


####################################################################################################
# temporary monkey-patches #########################################################################
####################################################################################################

# support for custom message on boundary constraint (https://www.logilab.org/ticket/288874)

@monkeypatch(BoundaryConstraint)
def __init__(self, op, boundary=None, msg=None):
    assert op in OPERATORS, op
    self.msg = msg
    self.operator = op
    self.boundary = boundary


@monkeypatch(BoundaryConstraint)
def failed_message(self, key, value):
    if self.msg:
        return self.msg, {}
    boundary = self.boundary
    if isinstance(boundary, Attribute):
        boundary = boundary.attr
    return "value %(KEY-value)s must be %(KEY-op)s %(KEY-boundary)s", {
        key + '-value': value,
        key + '-op': self.operator,
        key + '-boundary': boundary}


@monkeypatch(BoundaryConstraint)
def serialize(self):
    """simple text serialization"""
    value = u'%s %s' % (self.operator, self.boundary)
    if self.msg:
        value += '\n' + self.msg
    return value


@monkeypatch(BoundaryConstraint, methodname='deserialize')
@classmethod
def deserialize(cls, value):
    """simple text deserialization"""
    try:
        value, msg = value.split('\n', 1)
    except ValueError:
        msg = None
    op, boundary = value.split(' ', 1)
    return cls(op, eval(boundary), msg or None)


# monkey-patch for https://www.cubicweb.org/ticket/5352619 #########################################
# other part in views/patches.py

from cubicweb import neg_role  # noqa
from cubicweb.web import formfields  # noqa

orig_guess_field = formfields.guess_field


@monkeypatch(formfields)
def guess_field(eschema, rschema, role='subject', req=None, **kwargs):
    rdef = eschema.rdef(rschema, role)
    card = rdef.role_cardinality(role)
    composite = getattr(rdef, 'composite', None)
    # don't mark composite relation as required, we want the composite element to be removed when
    # not linked to its parent
    kwargs.setdefault('required', card in '1+' and composite != neg_role(role))
    return orig_guess_field(eschema, rschema, role, req, **kwargs)


# set eid on eschema during instance creation (https://www.cubicweb.org/ticket/10450092) ###########

from cubicweb import server  # noqa

orig_initialize_schema = server.initialize_schema


@monkeypatch(server)
def initialize_schema(config, schema, mhandler, event='create'):
    schema = mhandler.repo.schema
    orig_initialize_schema(config, schema, mhandler, event)


# backport warning instead of failure when some extentity has several value for an entity ##########
# to be removed once we depend on cw 3.23

from cubicweb.dataimport import importer  # noqa


@monkeypatch(importer.ExtEntity)
def prepare(self, schema, import_log):
    """Prepare an external entity for later insertion:

    * ensure attributes and inlined relations have a single value
    * turn set([value]) into value and remove key associated to empty set
    * remove non inlined relations and return them as a [(e1key, relation, e2key)] list

    The schema and import_log into which errors or warning may be emitted are given as
    arguments.

    Return a list of non inlined relations that may be inserted later, each relations defined by
    a 3-tuple (subject extid, relation type, object extid).

    Take care the importer may call this method several times.
    """
    assert self._schema is None, 'prepare() has already been called for %s' % self
    self._schema = schema
    eschema = schema.eschema(self.etype)
    deferred = []
    entity_dict = self.values
    for key, rtype, role in self.iter_rdefs():
        rschema = schema.rschema(rtype)
        if rschema.final or (rschema.inlined and role == 'subject'):
            if len(entity_dict[rtype]) > 1:
                values = ', '.join(repr(v) for v in entity_dict[rtype])
                import_log.record_warning(
                    "more than one value for attribute %r, only one will be kept: %s"
                    % (rtype, values), path=self.extid)
            if entity_dict[key]:
                entity_dict[rtype] = entity_dict[key].pop()
                if key != rtype:
                    del entity_dict[key]
                if (rschema.final and eschema.has_metadata(rtype, 'format')
                        and not rtype + '_format' in entity_dict):
                    entity_dict[rtype + '_format'] = u'text/plain'
            else:
                del entity_dict[key]
        else:
            for target_extid in entity_dict.pop(key):
                if role == 'subject':
                    deferred.append((self.extid, rtype, target_extid))
                else:
                    deferred.append((target_extid, rtype, self.extid))
    return deferred


@monkeypatch(importer.ExtEntitiesImporter)
def iter_ext_entities(self, ext_entities, deferred, queue):
    """Yield external entities in an order which attempts to satisfy
    schema constraints (inlined / cardinality) and to optimize the import.
    """
    schema = self.schema
    extid2eid = self.extid2eid
    for ext_entity in ext_entities:
        # check data in the transitional representation and prepare it for
        # later insertion in the database
        for subject_uri, rtype, object_uri in ext_entity.prepare(schema, self.import_log):
            deferred.setdefault(rtype, set()).add((subject_uri, object_uri))
        if not ext_entity.is_ready(extid2eid):
            queue.setdefault(ext_entity.etype, []).append(ext_entity)
            continue
        yield ext_entity
        # check for some entities in the queue that may now be ready. We'll have to restart
        # search for ready entities until no one is generated
        new = True
        while new:
            new = False
            for etype in self.etypes_order_hint:
                if etype in queue:
                    new_queue = []
                    for ext_entity in queue[etype]:
                        if ext_entity.is_ready(extid2eid):
                            yield ext_entity
                            # may unlock entity previously handled within this loop
                            new = True
                        else:
                            new_queue.append(ext_entity)
                    if new_queue:
                        queue[etype][:] = new_queue
                    else:
                        del queue[etype]


# datetime2ticks should support date as argument, else we get a tb with facets on agent ############
# (https://www.logilab.org/ticket/6060938)

from calendar import timegm  # noqa
from logilab.common import date  # noqa


@monkeypatch(date)
def datetime2ticks(somedate):
    return timegm(somedate.timetuple()) * 1000 + int(getattr(somedate, 'microsecond', 0) / 1000)
