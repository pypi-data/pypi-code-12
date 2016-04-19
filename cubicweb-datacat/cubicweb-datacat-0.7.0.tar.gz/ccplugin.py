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
"""cubicweb-datacat command plugins"""

from __future__ import print_function

from logilab.common.shellutils import ProgressBar

from cubicweb.cwctl import CWCTL
from cubicweb.toolsutils import Command
from cubicweb.utils import admincnx

from cubes.datacat import cwsource_pull_data
from cubes.datacat.vocabularies import ADMS_FRENCH_LABELS, LICENSE_SCHEME


class SyncSKOSSchemes(Command):
    """Synchronize SKOS schemes for a datacat instance.

    <instance>
      identifier of a datacat instance.

    """
    arguments = '<instance>'
    name = 'sync-schemes'
    min_args = 1
    max_args = 1

    def run(self, args):
        appid = args[0]
        with admincnx(appid) as cnx:
            rset = cnx.execute(
                'Any S ORDERBY X WHERE X is SKOSSource, X through_cw_source S')
            title = '-> synchronizing SKOS sources'
            pb = ProgressBar(len(rset), title=title)
            created, updated = set([]), set([])
            for eid, in rset:
                stats = cwsource_pull_data(cnx.repo, eid, raise_on_error=False)
                pb.update()
                created.update(stats['created'])
                updated.update(stats['updated'])
            # French translations
            qs = (u'Any C WHERE C cwuri IN ({0}), '
                  u'NOT EXISTS(L label_of C, L kind "preferred", L language_code "fr")'.format(
                      ', '.join([u"'{0}'".format(uri) for uri in ADMS_FRENCH_LABELS])))
            uri2eid = dict((concept.cwuri, concept.eid) for concept in cnx.execute(qs).entities())
            title = '-> Adding missing french labels for ADMS concepts'
            pb = ProgressBar(len(uri2eid), title=title)
            for concept_uri, concept_eid in uri2eid.items():
                fr_label = ADMS_FRENCH_LABELS.get(concept_uri)
                if fr_label:
                    label = cnx.create_entity('Label', label=fr_label, language_code=u'fr',
                                              kind=u'preferred', label_of=concept_eid)
                    created.add(label)
                pb.update()
            cnx.commit()
            print('\n   {0} created, {1} updated'.format(len(created), len(updated)))
            print('\n-> Adding constraints for license schemes')
            cnx.execute('SET CS scheme_relation RT WHERE CS cwuri %(scheme_uri)s, '
                        'RT name %(rtype_name)s',
                        {'scheme_uri': LICENSE_SCHEME, 'rtype_name': 'license_type'})
            cnx.commit()


CWCTL.register(SyncSKOSSchemes)
