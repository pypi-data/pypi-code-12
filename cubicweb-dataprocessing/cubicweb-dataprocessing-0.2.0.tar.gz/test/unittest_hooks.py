"""cubicweb-datacat test utilities"""

from cubicweb.devtools.testlib import CubicWebTC

from cubes.dataprocessing.test import (create_file, create_process,
                                       script_from_file, script_from_code)


class DataProcessWorkflowHooksTC(CubicWebTC):

    def _setup_and_start_dataprocess(self, cnx, process_etype, scriptcode):
        inputfile = create_file(cnx, 'data')
        script_kind = {
            'DataTransformationProcess': 'transformation',
            'DataValidationProcess': 'validation',
        }[process_etype]
        script = script_from_code(cnx, script_kind, scriptcode,
                                  name=u'%s script' % process_etype)
        process = create_process(cnx, process_etype, script)
        cnx.commit()
        process.cw_clear_all_caches()
        self.assertEqual(process.in_state[0].name,
                         'wfs_dataprocess_initialized')
        process.cw_set(process_input_file=inputfile)
        cnx.commit()
        process.cw_clear_all_caches()
        return process

    def test_data_process_autostart(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('ValidationScript', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=script)
            process = create_process(cnx, 'DataValidationProcess', script)
            cnx.commit()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_initialized')
            inputfile = create_file(cnx, 'data')
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_error')

    def test_data_process(self):
        with self.admin_access.repo_cnx() as cnx:
            for ptype in ('transformation', 'validation'):
                etype = 'Data' + ptype.capitalize() + 'Process'
                process = self._setup_and_start_dataprocess(cnx, etype, 'pass')
                self.assertEqual(process.in_state[0].name,
                                 'wfs_dataprocess_completed')
                process.cw_delete()
                cnx.commit()
                process = self._setup_and_start_dataprocess(cnx, etype, '1/0')
                self.assertEqual(process.in_state[0].name,
                                 'wfs_dataprocess_error')

    def test_data_process_output(self):
        with self.admin_access.repo_cnx() as cnx:
            self._setup_and_start_dataprocess(
                cnx, 'DataTransformationProcess',
                open(self.datapath('cat.py')).read())
            rset = cnx.execute(
                'Any X WHERE EXISTS(X produced_by S)')
            self.assertEqual(len(rset), 1)
            stdout = rset.get_entity(0, 0)
            self.assertEqual(stdout.read(), 'data\n')

    def test_data_process_stderr(self):
        with self.admin_access.repo_cnx() as cnx:
            proc = self._setup_and_start_dataprocess(
                cnx, 'DataValidationProcess', '1/0')
            self.assertIn('ZeroDivisionError', proc.process_stderr[0].read())

    def test_script_format(self):
        content = '\n'.join(['from __future__ import print_function',
                             'import sys',
                             'with open(sys.argv[1]) as f:',
                             '  print("<p>{0}</p>".format(f.read()), end="")'])
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('TransformationScript', name=u'HTML',
                                       implemented_by=create_file(cnx, content),
                                       output_format=u'text/html')
            cnx.commit()
            process = create_process(cnx, 'DataTransformationProcess', script)
            process.cw_set(process_input_file=create_file(cnx, 'blah'))
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(
                process.in_state[0].name, 'wfs_dataprocess_completed',
                process.process_stderr and process.process_stderr[0].read())
            rset = cnx.find('File', produced_by=process)
            output = rset.one()
            self.assertEqual(output.data_format, u'text/html')
            self.assertEqual(output.read(), '<p>blah</p>')

    def test_data_validation_process_validated_by(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('ValidationScript', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=script)
            process = create_process(cnx, 'DataValidationProcess', script)
            cnx.commit()
            inputfile = create_file(cnx, 'data')
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            validated = cnx.find('File', validated_by=process).one()
            self.assertEqual(validated, inputfile)

    def test_data_process_dependency(self):
        """Check data processes dependency"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = script_from_code(cnx, 'validation',
                                       'pass', u'v')
            vprocess = create_process(cnx, 'DataValidationProcess', vscript)
            cnx.commit()
            tscript = script_from_code(
                cnx, 'transformation',
                'import sys; sys.stdout.write(open(sys.argv[1]).read())', u't')
            tprocess = create_process(cnx, 'DataTransformationProcess',
                                      tscript)
            tprocess.cw_set(process_depends_on=vprocess)
            cnx.commit()
            inputfile = create_file(cnx, 'data')
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_completed'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_completed')
            rset = cnx.find('File', produced_by=tprocess)
            self.assertEqual(len(rset), 1, rset)
            output = rset.one()
            self.assertEqual(output.read(), inputfile.read())

    def test_data_process_dependency_validation_error(self):
        """Check data processes dependency: validation process error"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = script_from_code(cnx, 'validation', '1/0', u'v')
            vprocess = create_process(cnx, 'DataValidationProcess', vscript)
            cnx.commit()
            tscript = script_from_code(
                cnx, 'transformation',
                'import sys; print open(sys.argv[1]).read()', u't')
            tprocess = create_process(cnx, 'DataTransformationProcess',
                                      tscript)
            tprocess.cw_set(process_depends_on=vprocess)
            cnx.commit()
            inputfile = create_file(cnx, 'data')
            # Triggers "start" transition.
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_error'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_initialized')


class DataProcessWithSequenceTC(CubicWebTC):

    def test_script_sequence(self):
        with self.admin_access.repo_cnx() as cnx:
            s1 = script_from_file(cnx, 'transformation',
                                  self.datapath('reverse.py'))
            s2 = script_from_file(cnx, 'transformation',
                                  self.datapath('truncate.py'))
            seq = cnx.create_entity('TransformationSequence')
            cnx.create_entity('TransformationStep', index=2, step_script=s1,
                              in_sequence=seq)
            cnx.create_entity('TransformationStep', index=1, step_script=s2,
                              in_sequence=seq)
            cnx.commit()
            process = cnx.create_entity('DataTransformationProcess',
                                        transformation_sequence=seq)
            cnx.commit()
            inputfile = create_file(cnx, 'data')
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            rset = cnx.find('File', produced_by=process)
            self.assertEqual(len(rset), 1, rset)
            output = rset.one()
            self.assertEqual(output.read(), 'tad')


if __name__ == '__main__':
    import unittest
    unittest.main()
