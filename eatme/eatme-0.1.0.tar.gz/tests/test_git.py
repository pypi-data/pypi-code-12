# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

from plumbum import local

from eatme import git

rm = local['rm']['-r']
mkdir = local['mkdir']
git_clone = local['git']['clone']
git_config = local['git']['config']
git_checkout = local['git']['checkout']


class TestGIT(unittest.TestCase):
    TEST_REPO = 'git@github.com:kulapard/eatme.git'
    TEST_COMMIT = '0044406292d7e583cedc4be2113d36b48ad4e207'
    TEST_PATH = '/tmp/test_eatme_git_%s' % datetime.now().strftime('%s')

    def setUp(self):
        mkdir[self.TEST_PATH](retcode=[0, 1])
        git_clone[self.TEST_REPO][self.TEST_PATH]()
        with local.cwd(self.TEST_PATH):
            git_checkout[self.TEST_COMMIT]()

    def tearDown(self):
        rm[self.TEST_PATH]()

    def test_pull_update(self):
        self.assertIsNone(git.pull_update(path=self.TEST_PATH))
        self.assertIsNone(git.pull_update(path=self.TEST_PATH, branch='some_branch'))
        self.assertIsNone(git.pull_update(path=self.TEST_PATH, clean=True))
        self.assertIsNone(git.pull_update(path=self.TEST_PATH, branch='some_branch', clean=True))
        self.assertIsNone(git.pull_update(path='/fake_path'))

    def test_push(self):
        self.assertIsNone(git.push(path=self.TEST_PATH))
        self.assertIsNone(git.push(path=self.TEST_PATH, branch='some_branch'))
        self.assertIsNone(git.push(path=self.TEST_PATH, new_branch=True))
        self.assertIsNone(git.push(path=self.TEST_PATH, branch='some_branch', new_branch=True))
        self.assertIsNone(git.push(path='/fake_path'))


if __name__ == '__main__':
    unittest.main()
