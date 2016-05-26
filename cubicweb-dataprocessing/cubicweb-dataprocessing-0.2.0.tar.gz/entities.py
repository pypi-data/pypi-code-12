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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-dataprocessing entity's classes"""

import json
from subprocess import Popen, PIPE, list2cmdline
import sys

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity
from cubicweb.view import EntityAdapter


def process_type_from_etype(etype):
    """Return the type of data process from etype name"""
    return etype[len('Data'):-len('Process')].lower()


def fspath_from_eid(cnx, eid):
    """Return fspath for an entity with `data` attribute stored in BFSS"""
    # XXX this assumes the file is managed by BFSS.
    rset = cnx.execute('Any fspath(D) WHERE X data D, X eid %(feid)s',
                       {'feid': eid})
    if not rset:
        raise Exception('Could not find file system path for #%d.' % eid)
    return rset[0][0].read()


class TransformationStep(AnyEntity):
    __regid__ = 'TransformationStep'

    def dc_title(self):
        script = self.step_script[0]
        return u'[{0}] {1}'.format(self.index, script.dc_title())


class DataProcessAdapter(EntityAdapter):
    """Interface for data processes"""
    __regid__ = 'IDataProcess'
    __select__ = (EntityAdapter.__select__ &
                  is_instance('DataTransformationProcess',
                              'DataValidationProcess'))

    @property
    def process_type(self):
        """The type of data process"""
        return process_type_from_etype(self.entity.cw_etype)

    def fire_workflow_transition(self, trname, **kwargs):
        """Fire transition identified by *short* name `trname` of the
        underlying workflowable entity.
        """
        iwf = self.entity.cw_adapt_to('IWorkflowable')
        return iwf.fire_transition('wft_dataprocess_' + trname, **kwargs)

    def execute_script(self, script, inputfpath, outfile, parameters=None):
        """Execute script in a subprocess using ``inputfpath`` (file-path) and
        writting to `outfile`. Return subprocess return and subprocess stderr.
        """
        scriptpath = fspath_from_eid(self._cw, script.implemented_by[0].eid)
        cmdline = [sys.executable, scriptpath, inputfpath]
        if parameters:
            params = json.loads(parameters)
            for pname, pvalue in params.iteritems():
                if not isinstance(pvalue, unicode):
                    raise ValueError('invalid parameter value for "{0}": {1}, '
                                     'must be a string'.format(pname, pvalue))
                cmdline.extend(['--' + pname, pvalue])
        proc = Popen(cmdline, stdout=outfile, stderr=PIPE)
        self.info('starting subprocess with pid %s: %s',
                  proc.pid, list2cmdline(cmdline))
        _, stderrdata = proc.communicate()
        return proc.returncode, stderrdata

    @property
    def process_scripts(self):
        """Iterator on (script, parameters) for the data process."""
        if self.process_type == 'validation':
            return ((s, s.parameters) for s in self.entity.validation_script)
        else:
            rset = self._cw.execute(
                'Any S,P ORDERBY I ASC WHERE'
                ' STP index I, STP step_script S, STP parameters P,'
                ' STP in_sequence SQ, X transformation_sequence SQ,'
                ' X eid %(eid)s', {'eid': self.entity.eid})
            return ((self._cw.entity_from_eid(s), p) for s, p in rset)
