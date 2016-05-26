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

"""cubicweb-dataprocessing specific hooks and operations"""
import os
import os.path
import tempfile

from cubicweb import Binary
from cubicweb.predicates import (on_fire_transition, score_entity,
                                 objectify_predicate)
from cubicweb.server import hook
from cubicweb.server.sources import storages

from cubes.dataprocessing.entities import fspath_from_eid


class ServerStartupHook(hook.Hook):
    __regid__ = 'dataprocessing.serverstartup'
    events = ('server_startup', 'server_maintenance')

    def __call__(self):
        bfssdir = os.path.join(self.repo.config.appdatahome, 'bfss')
        if not os.path.exists(bfssdir):
            os.makedirs(bfssdir)
            print 'created', bfssdir
        storage = storages.BytesFileSystemStorage(bfssdir)
        storages.set_attribute_storage(self.repo, 'File', 'data', storage)


@objectify_predicate
def process_missing_dependency(cls, req, rset=None, eidfrom=None,
                               eidto=None, **kwargs):
    """Return 1 if the process has a dependency"""
    if not eidfrom:
        return 0
    if req.entity_metas(eidfrom)['type'] != 'DataTransformationProcess':
        return 0
    if req.execute('Any X WHERE EXISTS(X process_depends_on Y),'
                   '            X eid %(eid)s', {'eid': eidfrom}):
        return 1
    return 0


class AutoStartDataProcessHook(hook.Hook):
    """Automatically starts a data process when an input file is added."""
    __regid__ = 'datacat.dataprocess-start-when-inputfile-added'
    __select__ = (hook.Hook.__select__ &
                  hook.match_rtype('process_input_file') &
                  ~process_missing_dependency())

    events = ('after_add_relation', )
    category = 'workflow'

    def __call__(self):
        StartDataProcessOp.get_instance(self._cw).add_data(self.eidfrom)


def trinfo_concerns_a_dependency_process(trinfo):
    """Return 1 if the TrInfo concerns a data process which is a dependency of
    another.
    """
    process = trinfo.for_entity
    if process.cw_etype != 'DataValidationProcess':
        return 0
    return 1 if process.reverse_process_depends_on else 0


class StartDataProcessWithDependencyHook(hook.Hook):
    """Starts a data process when its dependency terminated successfully."""
    __regid__ = 'datacat.dataprocess-start-when-dependency-terminated'
    __select__ = (hook.Hook.__select__ &
                  on_fire_transition('DataValidationProcess',
                                     'wft_dataprocess_complete') &
                  score_entity(trinfo_concerns_a_dependency_process))

    events = ('after_add_entity', )
    category = 'workflow'

    def __call__(self):
        vprocess = self.entity.for_entity
        tprocess = vprocess.reverse_process_depends_on[0]
        StartDataProcessOp.get_instance(self._cw).add_data(tprocess.eid)


class StartDataProcessOp(hook.DataOperationMixIn, hook.LateOperation):
    """Trigger "start" transition for a data process.

    Use a LateOperation to ensure the workflow transition is fired after
    entity has a state.
    """

    def precommit_event(self):
        for eid in self.get_data():
            process = self.cnx.entity_from_eid(eid)
            iprocess = process.cw_adapt_to('IDataProcess')
            iprocess.fire_workflow_transition('start')


class StartDataProcessHook(hook.Hook):
    __regid__ = 'datacat.dataprocess-start'
    __select__ = (hook.Hook.__select__ &
                  (on_fire_transition('DataTransformationProcess',
                                      'wft_dataprocess_start') |
                   on_fire_transition('DataValidationProcess',
                                      'wft_dataprocess_start')))

    events = ('after_add_entity', )
    category = 'workflow'

    def __call__(self):
        process = self.entity.for_entity
        ExecuteProcessScriptsOp.get_instance(self._cw).add_data(process.eid)


class ExecuteProcessScriptsOp(hook.DataOperationMixIn, hook.Operation):
    """Run a subprocess for input file of the data process using its
    script(s). Then eventually attach the output file to the data process
    entity.
    """

    def precommit_event(self):
        for peid in self.get_data():
            process = self.cnx.entity_from_eid(peid)
            iprocess = process.cw_adapt_to('IDataProcess')
            if not process.process_input_file:
                msg = u'no input file'
                iprocess.fire_workflow_transition('error', comment=msg)
                return
            inputfile = process.process_input_file[0]
            inputfpath = fspath_from_eid(self.cnx, inputfile.eid)
            for idx, (script, params) in enumerate(iprocess.process_scripts):
                with tempfile.NamedTemporaryFile(delete=False) as outfile:
                    try:
                        returncode, stderr = iprocess.execute_script(
                            script, inputfpath, outfile, params)
                        if returncode:
                            msg = u'\n'.join(
                                ['error in transformation #%d of input file #%d' % (
                                    idx, inputfile.eid),
                                 'subprocess exited with status %d' % returncode])
                            self.cnx.create_entity(
                                'File', data=Binary(stderr), data_name=u'stderr',
                                data_format=u'text/plain',
                                reverse_process_stderr=process)
                            iprocess.fire_workflow_transition('error', comment=msg)
                            return
                    finally:
                        if idx >= 1:
                            os.remove(inputfpath)
                inputfpath = outfile.name
            if iprocess.process_type == 'transformation':
                output_format = script.output_format or inputfile.data_format
                with open(outfile.name) as output:
                    # XXX better copy the file rather than reading it...
                    self.cnx.create_entity(
                        'File', data=Binary(output.read()),
                        data_name=inputfile.data_name,
                        data_format=output_format,
                        produced_by=process)
            os.remove(outfile.name)
            iprocess.fire_workflow_transition('complete')


class SetValidatedByHook(hook.Hook):
    """Set the `validated_by` relation update completion of the data
    validation process.
    """
    __regid__ = 'datacat.datavalidationprocess-completed-inputfile-validated_by'
    __select__ = (hook.Hook.__select__ &
                  on_fire_transition('DataValidationProcess',
                                     'wft_dataprocess_complete'))

    events = ('after_add_entity', )
    category = 'workflow'

    def __call__(self):
        process = self.entity.for_entity
        self._cw.execute(
            'SET F validated_by VP WHERE F eid %(input)s, VP eid %(vp)s,'
            '                           NOT F validated_by VP',
            {'vp': process.eid,
             'input': process.process_input_file[0].eid})
