import os
import json
from unittest import TestCase
import boto3
from moto import mock_s3

from services.port_service import PortService
from services.account_storage_service import AccountStorageService
from task_template.test.test_base import MyBasicApp, MY_BASIC_APP_WF_DEF


class TestPortService(TestCase):

    def setUp(self):
        self.mock = mock_s3()
        self.mock.start()

        self.test_bucket = 'not_provided'
        self.test_account_id = 'not_provided'

        # Session creds don't matter because of the mock_s3 decorator
        test_session = boto3.session.Session(
            region_name='us-east-1'
        )
        self.s3 = test_session.client('s3')
        self.s3.create_bucket(Bucket=self.test_bucket)

        self.test_storage = AccountStorageService(session=test_session)
        
        self.test_wf = {
            "name": "test",
            "tasks": []
        }

        self.test_path = os.path.dirname(os.path.realpath(__file__))
        self.source_bundle = os.path.join(
            os.path.dirname(os.path.dirname(self.test_path)),
            'source_bundle'
        )
        os.makedirs(self.source_bundle)

    def tearDown(self):
        self.mock.stop()

        os.rmdir(self.source_bundle)

    def test_port_file_search(self):

        test_prefix = 'My/Test/Prefix'
        source_files = PortService._get_port_files(
            self.test_path,
            test_prefix
        )

        exp_result = (
            os.path.join(self.test_path, 'input', 'data', 'readme.txt'),
            '%s/%s' % (test_prefix, 'input/data/readme.txt')
        )
        self.assertIn(exp_result, source_files)

    def test_upload_port(self):
        """
        Test single task and port
        """

        new_path = os.path.join(self.test_path, 'input')

        test_task_def = MY_BASIC_APP_WF_DEF['tasks'][0]

        task_run_name = 'upload_test_run'

        # prefix is {task_name}/{port_name}
        test_prefix = '/'.join(
            ['not_provided', task_run_name,
             test_task_def['inputs'][0]['name']]
        )

        exp_results = [
            'data/readme.txt',
            'data/subsub/test.rst',
            'imgs/tester.png',
            '.DS_Store',
            'README.md',
            'app.py',
            # '__pycache__/app.cpython-27-PYTEST.pyc'
        ]

        with MyBasicApp() as app:

            app.task.second_port.value = new_path
            app.task.run_name = task_run_name

            port_service = PortService(
                app.task,
                storage_service=self.test_storage
            )

            port_service.upload_input_ports()

            new_task = port_service.task

            self.assertTrue(new_task.is_valid(remote=True))

            bucket_contents = self.s3.list_objects(Bucket=self.test_bucket)['Contents']
            print [key['Key'] for key in bucket_contents]
            count = 0
            for key in bucket_contents:
                self.assertEqual(len(bucket_contents), len(exp_results))
                for result in exp_results:
                    if key['Key'].endswith(result):
                        self.assertTrue(True)
                        count += 1

                self.assertIn(self.test_account_id, key['Key'])
                self.assertIn(test_prefix, key['Key'])

            self.assertEqual(count, len(bucket_contents))

            self.assertTrue(new_task.second_port.value.startswith(self.test_storage.location))
            self.assertTrue(new_task.second_port.value.endswith(test_prefix))

    def test_upload_ports(self):
        """
        Test multiple tasks and ports
        """

        new_path = os.path.join(self.test_path, 'input')

        with MyBasicApp() as app:

            app.task.second_port.value = new_path
            app.task.run_name = 'uploadss_test_run'

            port_service = PortService(
                app.task,
                storage_service=self.test_storage
            )


            port_service.upload_input_ports()

            new_task = port_service.task

            self.assertTrue(new_task.is_valid(remote=True))

            bucket_contents = self.s3.list_objects(Bucket=self.test_bucket)['Contents']

            count_files = [files for root, dirs, files in os.walk(new_path)]

            self.assertEqual(len(bucket_contents), sum([len(x) for x in count_files]))

            cnt_port1 = 0
            cnt_port2 = 0
            cnt_port3 = 0

            for key in bucket_contents:
                if 'port4' in key['Key']:
                    raise ValueError("Key name is incorrect %s" % key['Key'])
                if 'port1' in key['Key']:
                    cnt_port1 += 1
                if 'port2' in key['Key']:
                    cnt_port2 += 1
                if 'port3' in key['Key']:
                    cnt_port3 += 1

            self.assertTrue(cnt_port1 == cnt_port2 == cnt_port3)

    # def test_update_output_ports(self):
    #
    #     self.test_wf['tasks'].append(
    #         {
    #             "name": "task1",
    #             "inputs": [
    #                 {"name": "test_port", "value": os.path.join(self.test_path, 'input')}
    #             ],
    #             "outputs": [
    #                 {"name": "out1", "value": '{_s3_output_folder}/out1'},
    #                 {"name": "out2", "value": '{_s3_output_folder}/out2'},
    #                 {"name": "out3", "value": 'Not a directory port'}
    #             ]
    #         }
    #     )
    #
    #     port_service = PortService(
    #         json.dumps(self.test_wf),
    #         storage_service=self.test_storage
    #     )
    #
    #     test_prefix = '/'.join(
    #         [self.test_wf['name'], self.test_wf['tasks'][0]['name']]
    #     )
    #     print test_prefix
    #
    #     port_service.update_output_port_values()
    #
    #     new_workflow = port_service.workflow
    #
    #     output_ports = new_workflow['tasks'][0]['outputs']
    #
    #     s3_prefix = 's3://'
    #     for port in output_ports:
    #         if port['value'].startswith(s3_prefix):
    #             postfix = '/'.join([test_prefix, port['name']])
    #             self.assertTrue(port['value'].endswith(postfix))
