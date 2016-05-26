"""cubicweb-dataprocessing unit tests for entities"""
import json
import unittest

from cubicweb.devtools.testlib import CubicWebTC

from cubes.dataprocessing.entities import process_type_from_etype
from cubes.dataprocessing.test import (create_file, create_process,
                                       script_from_file)


class ProcessTypeTC(unittest.TestCase):

    def test_process_type_from_etype(self):
        for etype, ptype in [('DataTransformationProcess', 'transformation'),
                             ('DataValidationProcess', 'validation')]:
            self.assertEqual(process_type_from_etype(etype), ptype)


class TransformationSequenceTC(CubicWebTC):

    def test_script_sequence(self):
        with self.admin_access.repo_cnx() as cnx:
            s1 = cnx.create_entity('TransformationScript', name=u's1',
                                   implemented_by=create_file(cnx, 'pass'))
            s2 = cnx.create_entity('TransformationScript', name=u's2',
                                   implemented_by=create_file(cnx, 'pass'))
            seq = cnx.create_entity('TransformationSequence')
            cnx.create_entity('TransformationStep', index=2, step_script=s1,
                              parameters=u'{"foo": "bar"}',
                              in_sequence=seq)
            cnx.create_entity('TransformationStep', index=1, step_script=s2,
                              in_sequence=seq)
            proc = cnx.create_entity('DataTransformationProcess',
                                     transformation_sequence=seq)
            cnx.commit()
            scripts_params = proc.cw_adapt_to('IDataProcess').process_scripts
            expected = [(s2, None), (s1, u'{"foo": "bar"}')]
            self.assertEqual(list(scripts_params), expected)


class DataProcessAdapterTC(CubicWebTC):

    def test_script_with_parameter(self):
        """Check script parameters serialization."""
        with self.admin_access.repo_cnx() as cnx:
            script = script_from_file(cnx, 'transformation',
                                      self.datapath('iconv.py'))
            proc = create_process(cnx, 'DataTransformationProcess', script,
                                  parameters=u'{"from": "zorglub"}')
            inputfile = create_file(cnx, 'data', data_encoding=u'latin1')
            # Trigger "start" transition.
            proc.cw_set(process_input_file=inputfile)
            cnx.commit()
            proc.cw_clear_all_caches()
            # Just check that the script got correctly called (i.e. argument
            # parsing worked).
            self.assertEqual(proc.in_state[0].name, 'wfs_dataprocess_error')
            stderr = proc.process_stderr[0]
            self.assertIn('unknown encoding: zorglub', stderr.read())

    def test_script_with_parameter_invalid(self):
        params = {'from': 'ascii', 'to': {'a': 'b'}}
        with self.admin_access.repo_cnx() as cnx:
            script = script_from_file(
                cnx, 'transformation', self.datapath('iconv.py'))
            proc = create_process(cnx, 'DataTransformationProcess', script,
                                  parameters=json.dumps(params).decode('utf-8'))
            inputfile = create_file(cnx, 'data', data_encoding=u'latin1')
            # Trigger "start" transition.
            proc.cw_set(process_input_file=inputfile)
            with self.assertRaises(ValueError) as cm:
                cnx.commit()
            self.assertIn('invalid parameter', str(cm.exception))


if __name__ == '__main__':
    import unittest
    unittest.main()
