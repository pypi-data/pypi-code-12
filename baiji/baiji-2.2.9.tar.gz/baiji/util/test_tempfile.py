import os
import unittest
import shutil
import uuid
from test.test_support import EnvironmentVarGuard
from baiji.util import tempfile

class TestTempfile(unittest.TestCase):

    def test_that_NamedTemporaryFile_honors_TMP_env_var(self):
        env = EnvironmentVarGuard()
        test_temp_dir = 'test_tempfile_' + str(uuid.uuid4())
        env.set('BAIJI_TMP', test_temp_dir)
        with env:
            with tempfile.NamedTemporaryFile('w') as tf:
                self.assertEquals(os.path.dirname(tf.name), os.path.join(os.getcwd(), test_temp_dir))
        shutil.rmtree(test_temp_dir)
