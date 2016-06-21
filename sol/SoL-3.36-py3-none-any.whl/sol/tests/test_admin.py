# -*- coding: utf-8 -*-
# :Project:   SoL -- Test the admin script
# :Created:   dom 19 giu 2016 13:38:00 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from contextlib import redirect_stdout
from io import StringIO
from os import getcwd
from os.path import dirname, exists, join
from subprocess import run, PIPE
from tempfile import TemporaryDirectory
from unittest import TestCase


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        d = getcwd()
        while not exists(join(d, 'alembic')):
            d = dirname(d)
        cls.alembic_dir = join(d, 'alembic')
        cls.tmp_dir = TemporaryDirectory()
        cls.data_dir = cls.tmp_dir.name
        cls.sol_config = join(cls.data_dir, 'sol-config.ini')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.tmp_dir.cleanup()

    def do(self, *args, exit_status=0):
        from sol.scripts.admin import main

        out = StringIO()
        try:
            with redirect_stdout(out):
                main(args)
            return out.getvalue()
        except SystemExit as e:
            self.assertEqual(e.code, exit_status)

    def subdo(self, *args, exit_status=0):
        # This is needed because the admin script initializes the DBSession...
        cmd = ['soladmin']
        cmd.extend(args)
        res = run(cmd, stdout=PIPE)
        self.assertEqual(res.returncode, exit_status)
        return res.stdout


class TestAdminScript(BaseTestCase):
    def test_config_create(self):
        self.do("create-config",
                "--alembic-dir", self.alembic_dir,
                "-a", "ADMIN", "-p", "NIMDA12345",
                "-d", self.data_dir, self.sol_config)
        with open(self.sol_config) as f:
            content = f.read()
            self.assertIn('sqlite:///{datadir}/SoL.sqlite'.format(datadir=self.data_dir),
                          content)
            self.assertIn('sol.admin.user = ADMIN', content)
            self.assertIn('sol.admin.password = NIMDA12345', content)

    def test_config_update(self):
        self.do("update-config",
                "--alembic-dir", self.alembic_dir,
                "-a", "ADMIN0", "-p", "NIMDA23415",
                self.sol_config)
        with open(self.sol_config) as f:
            content = f.read()
            self.assertIn('sol.admin.user = ADMIN0', content)
            self.assertIn('sol.admin.password = NIMDA23415', content)

    def test_initialize_db(self):
        self.subdo("initialize-db", self.sol_config)

    def test_upgrade_db(self):
        self.subdo("upgrade-db", self.sol_config)
