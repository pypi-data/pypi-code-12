import os
import tarfile
import vcr
import shutil
from task_template.test.test_base import TestBase, MyBasicApp, MY_BASIC_APP_WF_DEF
from cloud_harness import AppController
from services.task_service import TaskService


class TestApp(TestBase):

    def setUp(self):
        self.DIRS_TO_REMOVE = []
        self.FILES_TO_REMOVE = []

    def test_get_filename_pos(self):
        app = AppController(None)

        # filename only.
        test_path1 = app._get_app_abs_path('app.py')
        exp_result1 = os.path.join(os.getcwd(), 'app.py')
        self.assertEqual(exp_result1, test_path1)

        # Test filename is absolute
        test_filename2 = os.path.abspath(__file__)
        test_path2 = app._get_app_abs_path(test_filename2)
        self.assertEqual(test_filename2, test_path2)

    def test_archive_pos_filter(self):
        test_path_dest = os.path.dirname(os.path.realpath(__file__))
        test_path_src = os.path.join(test_path_dest, 'input')

        filter_file = os.path.join(test_path_src, AppController.IGNORE_FILES_NAME)
        self.FILES_TO_REMOVE.append(filter_file)
        with open(filter_file, 'a') as f:
            f.write('imgs/\n')
            f.write('README.md\n')

        AppController._archive_source(test_path_src, test_path_dest)

        arch_tar = tarfile.open(os.path.join(test_path_dest, 'archive.tar.gz'))
        self.FILES_TO_REMOVE.append(arch_tar.name)
        filenames = arch_tar.getnames()
        self.assertIn('app.py', filenames)
        self.assertNotIn('README.md', filenames)
        self.assertIn('data/readme.txt', filenames)
        self.assertIn('data/subsub/test.rst', filenames)
        self.assertNotIn('imgs/tester.png', filenames)

    def test_archive_pos(self):

        test_path_dest = os.path.dirname(os.path.realpath(__file__))
        test_path_src = os.path.join(test_path_dest, 'input')

        AppController._archive_source(test_path_src, test_path_dest)

        arch_tar = tarfile.open(os.path.join(test_path_dest, 'archive.tar.gz'))
        self.FILES_TO_REMOVE.append(arch_tar.name)
        filenames = arch_tar.getnames()
        self.assertIn('app.py', filenames)
        self.assertIn('README.md', filenames)
        self.assertIn('data/readme.txt', filenames)
        self.assertIn('data/subsub/test.rst', filenames)
        self.assertIn('imgs/tester.png', filenames)

    @vcr.use_cassette('test/vcr_cassettes/gbdxtools.yaml')
    def test_get_gbdx_interface(self):

        with MyBasicApp() as app:
            task = app.task
            task_service = TaskService()
            task_service.register_task(task.json())

            task.run_name = 'this_run'

            workflow = AppController._get_gbdx_workflow_interface(task)
            wf_tasks = workflow.tasks

            self.assertListEqual(MY_BASIC_APP_WF_DEF.keys(), ['tasks', 'name'])
            self.assertEqual(len(wf_tasks), 2)
            self.assertEqual(len(MY_BASIC_APP_WF_DEF['tasks']), 2)
            self.assertEqual(wf_tasks[0].type, MY_BASIC_APP_WF_DEF['tasks'][0]['taskType'])
            self.assertEqual(wf_tasks[1].type, MY_BASIC_APP_WF_DEF['tasks'][1]['taskType'])
            self.assertEqual(len(wf_tasks[0].input_ports), 3)
            self.assertEqual(len(wf_tasks[0].output_ports), 1)

    def test_create_neg(self):

        bad_dir_names = [
            '/new_test_app',  # abs paths not allowed
            'my/dir',  # No path seperators allowed.
        ]

        args = {
            '--destination': None,
            '--download': False,
            '--remote': False,
            '--upload': False,
            '--verbose': False,
            '<file_name>': None,
            'create': True,
            'run': False
        }

        for baddir in bad_dir_names:
            args['<dir_name>'] = baddir
            app_ctrl = AppController(args)

            try:
                app_ctrl.invoke()
                self.assertTrue(False)
            except ValueError as e:
                self.assertTrue('Directory name is invalid' in e.message)

    def test_create_pos(self):

        curr_path = os.getcwd()
        dir_name = 'new_test_dir'
        dir_path = os.path.join(curr_path, dir_name)
        self.DIRS_TO_REMOVE.append(dir_path)

        args = {
            '--destination': None,
            '--download': False,
            '--remote': False,
            '--upload': False,
            '--verbose': False,
            '<file_name>': None,
            '<dir_name>': dir_name,
            'create': True,
            'run': False
        }

        app_ctrl = AppController(args)
        app_ctrl.invoke()

        exp_result = os.path.join(dir_path, AppController.DEFAULT_NEW_APP_FILENAME)

        self.assertTrue(os.path.isdir(dir_path))
        self.assertTrue(os.path.isfile(exp_result))

    def test_create_dest_neg(self):

        dir_name = 'new_test_dir'

        bad_destinations = [
            'relative/path',  # relative paths have to exist
            ''  # Empty string not allowed
        ]

        args = {
            '--download': False,
            '--remote': False,
            '--upload': False,
            '--verbose': False,
            '<file_name>': None,
            '<dir_name>': dir_name,
            'create': True,
            'run': False
        }

        for baddest in bad_destinations:
            args['--destination'] = baddest
            app_ctrl = AppController(args)

            try:
                app_ctrl.invoke()
                self.assertTrue(False)
            except ValueError as e:
                self.assertTrue('not a directory' in e.message or 'path is empty' in e.message)

    def test_create_dest_pos(self):
        # Test with relative destination.
        curr_path = os.getcwd()
        dir_name = 'new_test_dir'
        dest_name = os.path.join('test', 'input', 'data')
        dir_path = os.path.join(curr_path, dest_name, dir_name)
        self.DIRS_TO_REMOVE.append(dir_path)

        args = {
            '--destination': dest_name,
            '--download': False,
            '--remote': False,
            '--upload': False,
            '--verbose': False,
            '<file_name>': None,
            '<dir_name>': dir_name,
            'create': True,
            'run': False
        }

        app_ctrl = AppController(args)
        app_ctrl.invoke()

        exp_result = os.path.join(dir_path, AppController.DEFAULT_NEW_APP_FILENAME)

        self.assertTrue(os.path.isdir(dir_path))
        self.assertTrue(os.path.isfile(exp_result))

    def test_create_dest_pos_abs(self):
        # Test with absolute destination.
        dir_name = 'new_test_dir'
        dest_name = os.path.join(os.getcwd(), 'test', 'input', 'data')
        dir_path = os.path.join(dest_name, dir_name)
        self.DIRS_TO_REMOVE.append(dir_path)

        args = {
            '--destination': dest_name,
            '--download': False,
            '--remote': False,
            '--upload': False,
            '--verbose': False,
            '<file_name>': None,
            '<dir_name>': dir_name,
            'create': True,
            'run': False
        }

        app_ctrl = AppController(args)
        app_ctrl.invoke()

        exp_result = os.path.join(dir_path, AppController.DEFAULT_NEW_APP_FILENAME)

        self.assertTrue(os.path.isdir(dir_path))
        self.assertTrue(os.path.isfile(exp_result))

    def test_run_pos(self):

        filename = os.path.join('examples', 'echo_task', 'app.py')

        args = {
            '--destination': None,
            '--download': False,
            '--remote': False,
            '--upload': False,
            '--verbose': True,
            '<file_name>': filename,
            '<dir_name>': None,
            'create': False,
            'run': True
        }

        app_ctrl = AppController(args)
        app_ctrl.invoke()
        self.assertTrue(True)  # Test passes if no exception raised...

        # test with filename the doesn't exist
        args['<file_name>'] = 'does_not_exist.py'

        app_ctrl = AppController(args)

        try:
            app_ctrl.invoke()
        except ValueError as e:
            self.assertTrue('does not exist' in e.message)

    def tearDown(self):

        for filename in self.FILES_TO_REMOVE:
            self._remove_file(filename)

        for dirname in self.DIRS_TO_REMOVE:
            shutil.rmtree(dirname)

    @staticmethod
    def _remove_file(filename):

        if not os.path.isfile(filename):
            return

        os.remove(filename)
