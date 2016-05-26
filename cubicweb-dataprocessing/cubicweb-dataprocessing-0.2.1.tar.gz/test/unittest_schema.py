"""cubicweb-dataprocessing unit tests for schema"""

from cubicweb import ValidationError
from cubicweb.devtools import testlib

from cubes.dataprocessing.test import create_file


class TransformationSequenceTC(testlib.CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.file1_eid = create_file(cnx, 'pass').eid
            self.file2_eid = create_file(cnx, '1/0').eid
            self.script1_eid = cnx.create_entity(
                'TransformationScript', name=u's1',
                implemented_by=self.file1_eid).eid
            self.script2_eid = cnx.create_entity(
                'TransformationScript', name=u's2',
                implemented_by=self.file2_eid).eid
            cnx.commit()

    def test_index_constraint(self):
        """Check ('index', 'in_sequence') unique together constraint."""
        with self.admin_access.repo_cnx() as cnx:
            seq = cnx.create_entity('TransformationSequence')
            cnx.create_entity('TransformationStep', index=12,
                              in_sequence=seq,
                              step_script=self.script1_eid)
            cnx.commit()
            with self.assertRaises(ValidationError) as cm:
                cnx.create_entity('TransformationStep', index=12,
                                  in_sequence=seq,
                                  step_script=self.script2_eid)
                cnx.commit()
            cnx.rollback()
            self.assertIn('index is part of violated unicity constraint',
                          unicode(cm.exception))
            self.assertIn('in_sequence is part of violated unicity constraint',
                          unicode(cm.exception))
            # Distinct indices: OK.
            cnx.create_entity('TransformationStep', index=13,
                              in_sequence=seq,
                              step_script=self.script2_eid)
            cnx.commit()

    def test_item_script_constraint(self):
        """Check ('in_sequence', 'step_script') unique together constraint."""
        with self.admin_access.repo_cnx() as cnx:
            seq = cnx.create_entity('TransformationSequence')
            cnx.create_entity('TransformationStep', index=0,
                              in_sequence=seq,
                              step_script=self.script1_eid)
            cnx.commit()
            with self.assertRaises(ValidationError) as cm:
                cnx.create_entity('TransformationStep', index=1,
                                  in_sequence=seq,
                                  step_script=self.script1_eid)
                cnx.commit()
            cnx.rollback()
            self.assertIn('step_script is part of violated unicity constraint',
                          unicode(cm.exception))
            self.assertIn('in_sequence is part of violated unicity constraint',
                          unicode(cm.exception))
            # Distinct indices: OK.
            cnx.create_entity('TransformationStep', index=1,
                              in_sequence=seq,
                              step_script=self.script2_eid)
            cnx.commit()


if __name__ == '__main__':
    import unittest
    unittest.main()
