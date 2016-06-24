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

from cubicweb import cwvreg
from cubicweb.cwconfig import register_persistent_options
from cubicweb.uilib import PRINTERS

from cubes.skos import rdfio
from cubes.skos.ccplugin import ImportSkosData

from cubes.saem_ref import cwuri_url
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
    from cubicweb.dataimport.massive_store import MassiveObjectStore
    from cubes.saem_ref.sobjects.skos import SAEMMetadataGenerator
    return MassiveObjectStore(cnx, metagen=SAEMMetadataGenerator(cnx))


def _nohook_store_factory(cnx):
    from cubicweb.dataimport.stores import NoHooRQLObjectStore
    from cubes.saem_ref.sobjects.skos import SAEMMetadataGenerator
    return NoHooRQLObjectStore(cnx, metagen=SAEMMetadataGenerator(cnx))


ImportSkosData.cw_store_factories['massive'] = _massive_store_factory
ImportSkosData.cw_store_factories['nohook'] = _nohook_store_factory


####################################################################################################
# temporary monkey-patches #########################################################################
####################################################################################################

from yams.constraints import Attribute, BoundaryConstraint, cstr_json_loads  # noqa


@monkeypatch(BoundaryConstraint, methodname='deserialize')
@classmethod
def deserialize(cls, value):
    """simple text deserialization"""
    try:
        values = cstr_json_loads(value)
        return cls(**values)
    except ValueError:
        try:
            value, msg = value.split('\n', 1)
        except ValueError:
            msg = None
        op, boundary = value.split(' ', 1)
        return cls(op, eval(boundary), msg or None)
