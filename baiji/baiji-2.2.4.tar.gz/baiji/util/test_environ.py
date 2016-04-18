import os
import unittest
import uuid

class EnvironGetEnvPath(unittest.TestCase):

    def test_that_getenvpath_reads_from_env(self):
        from baiji.util.environ import getenvpath
        env_var = str(uuid.uuid4())
        os.environ[env_var] = 'foo'
        self.assertEquals(getenvpath(env_var, 'bar'), os.path.abspath('foo'))

    def test_that_getenvpath_supports_default(self):
        from baiji.util.environ import getenvpath
        env_var = str(uuid.uuid4())
        self.assertEquals(getenvpath(env_var, 'bar'), os.path.abspath('bar'))

    def test_that_getenvpath_expands_user_home(self):
        from baiji.util.environ import getenvpath
        env_var = str(uuid.uuid4())
        os.environ[env_var] = '~/foo'
        self.assertEquals(os.environ.get(env_var, 'bar'), '~/foo')
        self.assertEquals(getenvpath(env_var, 'bar'), os.path.expanduser('~/foo'))
