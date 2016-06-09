import datetime
import json
import re
from collections import namedtuple

import mock
import pandas as pd
import pytest
import responses
import six

from datarobot import (Project,
                       Blueprint,
                       AUTOPILOT_MODE,
                       Model,
                       ModelJob,
                       Featurelist,
                       PredictJob,
                       RecommenderSettings,
                       AdvancedOptions,
                       UserCV,
                       UserTVH,
                       QUEUE_STATUS,
                       errors)
from datarobot.enums import SCORING_TYPE
from datarobot.errors import DataRobotDeprecationWarning

from .test_helpers import URLParamsTestCase, fixture_file_path
from .utils import SDKTestcase, assertJsonEq, warns

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

AIMED_PROJECT_JSON = """
{
    "id": "p-id",
    "projectName": "Untitled Project",
    "fileName": "Untitled Project.csv",
    "stage": "modeling",
    "autopilotMode": 0,
    "created": "2015-05-21T16:02:02.573565",
    "target": "SalePrice",
    "metric": "Gamma Deviance",
    "partition": {
        "cvMethod": "random",
        "validationType": "CV",
        "validationPct": null,
        "holdoutPct": 20,
        "reps": 5,
        "holdoutLevel": null,
        "validationLevel": null,
        "trainingLevel": null,
        "partitionKeyCols": null,
        "userPartitionCol": null,
        "cvHoldoutLevel": null,
        "datetimeCol": null
    },
    "recommender": {
        "isRecommender": false,
        "recommenderItemId": null,
        "recommenderUserId": null
    },
    "advancedOptions": {
        "weights": null,
        "blueprintThreshold": null,
        "responseCap": null,
        "seed": null
    },
    "positiveClass": null,
    "maxTrainPct": 64,
    "holdoutUnlocked": true,
    "targetType": "Regression"
}
"""


class TestWaitForAsyncStatus(SDKTestcase):

    def setUp(self):
        super(TestWaitForAsyncStatus, self).setUp()
        self.url = 'https://host_name.com/status/status-id/'
        response = namedtuple('response', ['headers'])
        self.response = response(headers={'Location': self.url})

    @responses.activate
    def test_timeout(self):
        responses.add(
            responses.GET,
            self.url,
            content_type='application/json',
            status=200,
            body=json.dumps({}),
        )

        with self.assertRaises(errors.AsyncTimeoutError):
            Project.from_async(self.url, max_wait=1)

    @responses.activate
    def test_check_failed(self):
        """
        Getting status_code different from 200 and 303 should raise AsyncFailureError
        """
        responses.add(
            responses.GET,
            self.url,
            content_type='application/json',
            status=504,
            body=json.dumps({}),
        )

        with self.assertRaises(errors.AsyncFailureError):
            Project.from_async(self.url, max_wait=1)

    @responses.activate
    def test_check_exception_for_failure_contains_status_code_and_async_location(self):
        """
        Getting status_code different from 200 and 303 should raise AsyncFailureError
        """
        responses.add(
            responses.GET,
            self.url,
            content_type='application/json',
            status=504,
            body=json.dumps({}),
        )

        with self.assertRaises(errors.ProjectAsyncFailureError) as e:
            Project.from_async(self.url, max_wait=1)
            self.assertEqual(e.status_code, 504)
            self.assertEqual(e.async_location, self.url)

    @responses.activate
    def test_project_creation_failed(self):
        response_dict = {
            'status': 'ERROR',
        }
        responses.add(
            responses.GET,
            self.url,
            content_type='application/json',
            status=200,
            body=json.dumps(response_dict),
        )

        with self.assertRaises(errors.AsyncProcessUnsuccessfulError):
            Project.from_async(self.url, max_wait=1)

    @responses.activate
    def test_project_creation_aborted(self):
        response_dict = {
            'status': 'ABORTED',
        }
        responses.add(
            responses.GET,
            self.url,
            content_type='application/json',
            status=200,
            body=json.dumps(response_dict),
        )

        with self.assertRaises(errors.AsyncProcessUnsuccessfulError):
            Project.from_async(self.url, max_wait=1)


class TestProjectTrainRoute(SDKTestcase):

    def setUp(self):
        super(TestProjectTrainRoute, self).setUp()
        self.return_body = json.dumps({'model_id': '5223deadbeefdeadbeef0123'})

    @responses.activate
    def test_async_flow(self):
        project_data = {'id': 'p-id',
                        'project_name': 'project_test_name',
                        'mode': 2,
                        'stage': 'stage',
                        'target': 'test_target'}
        job_data = {'status': 'inprogress',
                    'samplePct': 64.0,
                    'processes': ['One-Hot Encoding',
                                  'Missing Values Imputed',
                                  'Standardize',
                                  'Linear Regression'],
                    'modelType': 'Linear Regression',
                    'featurelistId': '55666d05100d2b01a1104dae',
                    'blueprintId': '3bb4665320be633b30a9601b3e73284d',
                    'projectId': '55666eb9100d2b109b59e267',
                    'id': 12,
                    'modelId': '55666d0d100d2b01b1104db4'}

        p = Project(project_data)

        responses.add(
            responses.POST,
            'https://host_name.com/projects/p-id/models/',
            content_type='application/json',
            status=202,
            body='',
            adding_headers={'Location': 'https://host_name.com/projects/p-id/modelJobs/12/'}
        )
        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/modelJobs/12/',
            content_type='application/json',
            status=200,
            body=json.dumps(job_data)
        )

        blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
        retval = p.train(blueprint_id)
        self.assertEqual(retval, '12')

    def test_print_project_from_id(self):
        project = Project('some-project-id')
        print(project)  # checks that method relevant to print works on this (failed in one release)

    @responses.activate
    def test_all_defaults(self):

        data = {'id': 'p-id',
                'project_name': 'project_test_name',
                'mode': 2,
                'stage': 'stage',
                'target': 'test_target'}
        p = Project(data)

        responses.add(
            responses.POST,
            'https://host_name.com/projects/p-id/models/',
            content_type='application/json',
            status=201,
            body='',
            adding_headers={'Location': 'http://pam/api/v2/projects/p-id/models/id/'}
        )
        blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
        model_id = p.train(blueprint_id)
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/')
        self.assertEqual('id', model_id)

    @responses.activate
    def test_no_defaults(self):

        data = {'id': 'p-id',
                'project_name': 'project_test_name',
                'mode': 2,
                'stage': 'stage',
                'target': 'test_target'}
        p = Project(data)

        responses.add(
            responses.POST,
            'https://host_name.com/projects/p-id/models/',
            content_type='application/json',
            status=201,
            body='',
            adding_headers={'Location': 'http://pam/api/v2/projects/p-id/models/id/'}
        )
        blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
        dataset_id = '5223deadbeefdeadbeef0101'
        source_project_id = '5223deadbeefdeadbeef1234'
        scoring_type = SCORING_TYPE.cross_validation
        sample_pct = 44

        p.train(blueprint_id,
                featurelist_id=dataset_id,
                source_project_id=source_project_id,
                sample_pct=sample_pct,
                scoring_type=scoring_type)
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/')
        request = json.loads(responses.calls[0].request.body)
        self.assertEqual(request['blueprintId'], blueprint_id)
        self.assertEqual(request['sourceProjectId'], source_project_id)
        self.assertEqual(request['featurelistId'], dataset_id)
        self.assertEqual(request['samplePct'], sample_pct)
        self.assertEqual(request['scoringType'], scoring_type)

    @responses.activate
    def test_with_trainable_object_ignores_any_source_project_id(self):

        data = {'id': 'p-id',
                'project_name': 'project_test_name',
                'mode': 2,
                'stage': 'stage',
                'target': 'test_target'}
        p = Project(data)

        responses.add(
            responses.POST,
            'https://host_name.com/projects/p-id/models/',
            content_type='application/json',
            status=201,
            body='',
            adding_headers={'Location': 'http://pam/api/v2/projects/p-id/models/id/'}
        )
        blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
        source_project_id = '5223deadbeefdeadbeef1234'

        data = dict(id=blueprint_id,
                    project_id=source_project_id,
                    model_type='Pretend Model',
                    processes=['Cowboys', 'Aliens'])

        blueprint = Blueprint(data)

        p.train(blueprint,
                source_project_id='should-be-ignored')
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/')
        request = json.loads(responses.calls[0].request.body)
        self.assertEqual(request['blueprintId'], blueprint_id)
        self.assertEqual(request['sourceProjectId'], source_project_id)


class ProjectTestCase(SDKTestcase):

    def prep_successful_project_creation_responses(self,
                                                   project_id='p-id'):
        """
        Setup the responses library to mock calls to the API necessary to
        create a project

        Parameters
        ----------
        project_id : str
            The mocked project's supposed id
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/',
                      body='',
                      status=202,
                      content_type='application/json',
                      adding_headers={'Location': 'https://host_name.com/status/status-id/'}
                      )
        responses.add(responses.GET,
                      'https://host_name.com/status/status-id/',
                      status=303,
                      body='',
                      content_type='application/json',
                      adding_headers={
                          'Location': 'https://host_name.com/projects/{}/'.format(project_id)}
                      )
        responses.add(responses.GET,
                      'https://host_name.com/projects/{}/'.format(project_id),
                      status=200,
                      body=AIMED_PROJECT_JSON,
                      content_type='application/json')

    def prep_successful_aim_responses(self,
                                      project_id='p-id',
                                      project_info=AIMED_PROJECT_JSON):
        """A helper to use with setting up test scenarios where the server is
        expected to successfully set the target.

        Parameters
        ----------
        project_id : str
            The ID from the mocked project under test
        project_info : str
            JSON of the information describing the final result of the
            project after the set_target call succeeds.
        """
        project_url = 'https://host_name.com/projects/{}/'.format(project_id)
        aim_url = project_url + 'aim/'

        responses.add(responses.PATCH,
                      aim_url,
                      body='',
                      status=202,
                      adding_headers={'Location': 'https://host_name.com/status/some-status/'},
                      content_type='application/json')

        responses.add(responses.GET,
                      'https://host_name.com/status/some-status/',
                      body='',
                      status=303,
                      adding_headers={'Location': project_url},
                      content_type='application/json')
        responses.add(responses.GET,
                      project_url,
                      body=project_info,
                      status=200,
                      content_type='application/json')

    def test_instantiation_with_data(self):
        """
        Test instantiation Project(data)
        """
        data = {'id': 'project_id',
                'project_name': 'project_test_name',
                'mode': 2,
                'stage': 'stage',
                'target': 'test_target'}
        project_inst = Project(data)
        self.assertEqual(project_inst.id, data['id'])
        self.assertEqual(project_inst.project_name, data['project_name'])
        self.assertEqual(project_inst.mode, data['mode'])
        self.assertEqual(project_inst.stage, data['stage'])
        self.assertEqual(project_inst.target, data['target'])

        self.assertEqual(repr(project_inst), 'Project(project_test_name)')

        data = {'id': 'project_id',
                'project_name': 'project_test_name',
                'mode': 2,
                'stage': 'stage',
                'target': {'target_name': 'test_target'}}
        project_inst = Project(data)
        self.assertEqual(project_inst.target, data['target']['target_name'])

    def test_print_project_nonascii_name(self):
        project = Project({'id': 'project-id', 'project_name': u'\u3053\u3093\u306b\u3061\u306f'})
        print(project)

    def test_get_permalink(self):
        p = Project('pid')
        expected = 'https://host_name.com/projects/pid/models'
        self.assertEqual(expected, p.get_leaderboard_ui_permalink())

    @mock.patch('webbrowser.open')
    def test_open_leaderboard_browser(self, webbrowser_open):
        project = Project('p-id')
        project.open_leaderboard_browser()
        self.assertTrue(webbrowser_open.called)

    @responses.activate
    def test_create_project_async(self):
        self.prep_successful_project_creation_responses()

        new_project = Project.create(sourcedata='https://google.com')
        self.assertEqual(new_project.id, 'p-id')
        self.assertEqual(new_project.project_name, 'Untitled Project')

    @responses.activate
    def test_create_project_non_ascii_async(self):
        self.prep_successful_project_creation_responses()
        name = u'\xe3\x81\x82\xe3\x81\x82\xe3\x81\x82'
        Project.create("https://google.com", project_name=name)

    @responses.activate
    def test_get_project_metrics(self):
        """
        Test get project metrics
        """
        raw = """
        {"available_metrics":
            ["Gini Norm",
              "Weighted Gini Norm",
              "Weighted R Squared",
              "Weighted RMSLE",
              "Weighted MAPE",
              "Weighted Gamma Deviance",
              "Gamma Deviance",
              "RMSE",
              "Weighted MAD",
              "Tweedie Deviance",
              "MAD",
              "RMSLE",
              "Weighted Tweedie Deviance",
              "Weighted RMSE",
              "MAPE",
              "Weighted Poisson Deviance",
              "R Squared",
              "Poisson Deviance"],
         "feature_name": "SalePrice"}
        """
        expected_url = 'https://host_name.com/projects/p-id/features/metrics/'
        responses.add(responses.GET,
                      expected_url,
                      body=raw,
                      status=200,
                      content_type='application/json')
        get_project = Project('p-id').get_metrics('SalePrice')
        self.assertEqual(responses.calls[0].request.url,
                         expected_url + '?featureName=SalePrice')
        self.assertEqual(get_project["feature_name"], 'SalePrice')

    @responses.activate
    def test_get_project(self):
        """
        Test get project
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/',
                      body=AIMED_PROJECT_JSON,
                      status=200,
                      content_type='application/json')
        get_project = Project.get('p-id')
        self.assertEqual(get_project.id, 'p-id')
        self.assertEqual(get_project.project_name, 'Untitled Project')
        self.assertEqual(get_project.target, 'SalePrice')
        self.assertEqual(get_project.target_type, 'Regression')
        self.assertEqual(get_project.stage, 'modeling')
        self.assertEqual(get_project.metric, 'Gamma Deviance')
        self.assertIsNone(get_project.positive_class)
        self.assertEqual(get_project.max_train_pct, 64)
        self.assertTrue(get_project.holdout_unlocked)
        self.assertIsInstance(get_project.partition, dict)
        self.assertIsInstance(get_project.recommender, dict)
        self.assertIsInstance(get_project.advanced_options, dict)

        self.assertIsInstance(get_project.created, datetime.datetime)

    @responses.activate
    def test_delete_project(self):
        """
        Test delete project
        """
        responses.add(responses.DELETE,
                      'https://host_name.com/projects/p-id/',
                      status=204)

        project = Project('p-id')
        del_result = project.delete()
        self.assertEquals(responses.calls[0].request.method, 'DELETE')
        self.assertIsNone(del_result)

    @responses.activate
    def test_update_project(self):
        """
        Test update project
        """
        raw = """
        {
            "status": "OK",
            "changes": {
                "project_name": "new name"
            }
        }
        """
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body=raw,
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        with warns(DataRobotDeprecationWarning):
            assert project.update(project_name='new name') is project
        assert responses.calls[0].request.method == 'PATCH'
        assert project.project_name == 'new name'

    def test_bad_update(self):
        with pytest.raises(TypeError):
            Project('p-id').update(name='new name')

    @patch('os.path.isfile')
    def test_non_ascii_filename(self, isfile_mock):
        isfile_mock.return_value = True
        bad_filename = u'\xc3\x98.csv'
        with pytest.raises(errors.IllegalFileName):
            Project.create(bad_filename)

    @responses.activate
    def test_rename(self):
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        project.rename('new name')
        assert responses.calls[0].request.method == 'PATCH'
        payload = json.loads(responses.calls[0].request.body)
        assert project.project_name == payload['projectName'] == 'new name'

    @responses.activate
    def test_unlock_holdout(self):
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        upd_data = project.unlock_holdout()
        self.assertEquals(responses.calls[0].request.method, 'PATCH')
        payload = json.loads(responses.calls[0].request.body)
        self.assertTrue(payload['holdoutUnlocked'])
        self.assertTrue(upd_data)

    @responses.activate
    def test_set_worker_count(self):
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        project.set_worker_count(20)
        self.assertEquals(responses.calls[0].request.method, 'PATCH')
        payload = json.loads(responses.calls[0].request.body)
        self.assertTrue(payload['workerCount'])

    @responses.activate
    def test_by_upload_file_path(self):
        """
        Project.create(
            'synthetic-100.csv')
        """
        self.prep_successful_project_creation_responses()
        path = fixture_file_path('synthetic-100.csv')

        Project.create(path)
        # decoded to str implicitly
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message.to_string())

    def test_by_upload_file_path_fail(self):
        """
        Bad file name: Project.create('meh.csv')
        """
        path = fixture_file_path('does_not_exist.csv')
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(path)

    @responses.activate
    def test_by_upload_file_content(self):
        """
        Project.create(b'lalalala')
        """
        self.prep_successful_project_creation_responses()

        content_line = six.b('one,two\n' + '1,2'*100)
        Project.create(content_line)
        # decoded to str implicitly
        request_message = responses.calls[0].request.body
        self.assertIn(content_line, request_message.to_string())

    def test_by_upload_content_encoding(self):
        """
        Bad content encoding Project.create(u'lalalala')
        """
        content_line = u'lalalala'
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(content_line)

    @responses.activate
    def test_by_upload_from_fd(self):
        """
        Project.create(
          sourcedata=open('synthetic-100.csv'))
        """
        self.prep_successful_project_creation_responses()

        path = fixture_file_path('synthetic-100.csv')

        with open(path, 'rb') as fd:
            Project.create(sourcedata=fd)
            request_message = responses.calls[0].request.body

            with open(path, 'rb') as fd2:
                self.assertIn(fd2.read(), request_message.to_string())

        file_like = six.StringIO('thra\ntata\nrata')
        Project.create(
            sourcedata=file_like)

        # decoded to str implicitly
        request_message = responses.calls[3].request.body
        self.assertIn(six.b('thra\ntata\nrata'), request_message.to_string())

    @responses.activate
    def test_by_upload_file_seek(self):
        """
        Seek to EOF Project.create(
            open('synthetic-100.csv')
        """
        self.prep_successful_project_creation_responses()

        path = fixture_file_path('synthetic-100.csv')
        with open(path, 'rb') as fd:
            fd.seek(20000000)
            Project.create(fd)
            # decoded to str implicitly

            request_message = responses.calls[0].request.body
            with open(path, 'rb') as fd2:
                self.assertIn(fd2.read(), request_message.to_string())

    @responses.activate
    def test_by_upload_file_closed(self):
        """
        Closed fd Project.create(
            open('synthetic-100.csv')
        """
        path = fixture_file_path('synthetic-100.csv')
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/upload/',
                      body='',
                      status=200,
                      )
        fd = open(path)
        fd.close()
        with self.assertRaises(ValueError):
            Project.create(fd)

    @responses.activate
    def test_upload_by_file_url(self):
        """
        Project.create('http:/google.com/datarobot.csv')
        """
        self.prep_successful_project_creation_responses()

        link = 'http:/google.com/datarobot.csv'
        Project.create(sourcedata=link)
        request_message = responses.calls[0].request.body
        assertJsonEq(
            request_message,
            json.dumps(
                {"url": link, "projectName": "Untitled Project"}
            )
        )
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')

    @responses.activate
    def test_set_target(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        self.prep_successful_aim_responses('p-id',
                                           project_info=AIMED_PROJECT_JSON)
        opts = AdvancedOptions(weights='WeightName')
        upd_project = Project('p-id').set_target(
            'SalePrice',
            metric='RMSE',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'metric': 'RMSE',
            'weights': 'WeightName'
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_target_price(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        self.prep_successful_aim_responses('p-id',
                                           project_info=AIMED_PROJECT_JSON)
        upd_project = Project('p-id').set_target('SalePrice')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
        }))
        self.assertEqual(upd_project.metric, 'Gamma Deviance')

    @responses.activate
    def test_set_target_async_error(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/aim/',
                      body='',
                      status=202,
                      adding_headers={'Location': 'https://host_name.com/projects/p-id/'},
                      content_type='application/json')

        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/',
                      body=json.dumps({'status': 'ERROR'}),
                      status=200,
                      content_type='application/json')
        with self.assertRaises(errors.AsyncProcessUnsuccessfulError):
            Project('p-id').set_target(
                'SalePrice',
                metric='RMSE',
            )
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')

    def test_advanced_options_must_be_object(self):
        with self.assertRaises(TypeError):
            Project('p-id').set_target(
                'SalePrice',
                advanced_options={'garbage': 'in'}
            )

    def test_blueprint_threshold_must_be_int(self):
        with self.assertRaises(ValueError):
            opts = AdvancedOptions(blueprint_threshold='some string')
            Project('p-id').set_target(
                'SalePrice',
                advanced_options=opts)

    @responses.activate
    def test_set_blueprint_threshold(self):
        """
        Set blueprint threshold
        """
        self.prep_successful_aim_responses(project_id='p-id')

        opts = AdvancedOptions(blueprint_threshold=2)
        upd_project = Project('p-id').set_target(
            'SalePrice',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'blueprintThreshold': 2,
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    def test_response_cap_value_must_be_float(self):
        with self.assertRaises(ValueError):
            opts = AdvancedOptions(response_cap='some string')
            Project('p-id').set_target(
                'SalePrice',
                # blueprint threshold must be float
                advanced_options=opts)

    @responses.activate
    def test_set_response_cap(self):
        """
        Set Response Cap
        """
        self.prep_successful_aim_responses('p-id')

        opts = AdvancedOptions(response_cap=0.7)
        upd_project = Project('p-id').set_target(
            'SalePrice',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'responseCap': 0.7,
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_seed(self):
        """
        Set Response Cap
        """
        self.prep_successful_aim_responses('p-id')

        opts = AdvancedOptions(seed=22)
        upd_project = Project('p-id').set_target(
            'SalePrice',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'seed': 22,
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_target_recommender(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        self.prep_successful_aim_responses('p-id')

        with self.assertRaisesRegexp(TypeError, 'settings should be a RecommenderSettings'):
            Project('p-id').set_target(
                'SalePrice',
                # lists is not accepted
                recommender_settings=['User_col', 'Item_col'])
        with self.assertRaisesRegexp(TypeError, 'settings should be a RecommenderSettings'):
            Project('p-id').set_target(
                'SalePrice',
                # dict either
                recommender_settings={'user_id': 'User_col', 'item_id': 'Item_col'})
        rec_settings = RecommenderSettings('User_col', 'Item_col')
        upd_project = Project('p-id').set_target(
            'SalePrice',
            recommender_settings=rec_settings)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'recommenderUserId': 'User_col',
            'recommenderItemId': 'Item_col',
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_target_advance_partition_method_cv(self):
        """
        Set project with advanced partition method
        """
        self.prep_successful_aim_responses(project_id='p-id')

        part_method = UserCV(user_partition_col='NumPartitions',
                             cv_holdout_level=1, seed=42)
        p = Project('p-id').set_target(
            'SalePrice',
            partitioning_method=part_method)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'userPartitionCol': 'NumPartitions',
            'cvHoldoutLevel': 1,
            'seed': 42,
            'validationType': 'user',
            'cvMethod': 'CV'
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_advance_partition_method_tvh(self):
        """
        Set project with advanced partition method
        """
        self.prep_successful_aim_responses(project_id='p-id')
        part_method = UserTVH(user_partition_col='NumPartitions',
                              validation_level=1, training_level=2,
                              holdout_level=3,
                              seed=42)
        p = Project('p-id').set_target(
            'SalePrice',
            partitioning_method=part_method)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'userPartitionCol': 'NumPartitions',
            'holdoutLevel': 3,
            'seed': 42,
            'validationLevel': 1,
            'trainingLevel': 2,
            'validationType': 'TVH',
            'cvMethod': 'user'
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_specify_positive_class(self):
        """
        Set project with advanced partition method
        """
        self.prep_successful_aim_responses(project_id='p-id')

        p = Project('p-id').set_target(
            'Forks',
            positive_class='None or Unspecified')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'Forks',
            'positiveClass': 'None or Unspecified',
            'mode': AUTOPILOT_MODE.FULL_AUTO
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_specify_quickrun(self):
        """
        Set project with quickrun option
        """
        self.prep_successful_aim_responses(project_id='p-id')

        p = Project('p-id').set_target(
            'Forks',
            quickrun=True)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'Forks',
            'quickrun': True,
            'mode': AUTOPILOT_MODE.FULL_AUTO
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    def test_pass_advance_part_wrong(self):
        with self.assertRaises(TypeError):
            Project('p-id').set_target(
                'SalePrice',
                partitioning_method={'CV': 'TVH'})

    @responses.activate
    def test_pause_autopilot(self):
        """
        Project('p-id').pause_autopilot()
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilot/',
                      body='',
                      status=202,
                      content_type='application/json')
        self.assertTrue(Project('p-id').pause_autopilot())
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'command': 'stop'
        }))

    @responses.activate
    def test_unpause_autopilot(self):
        """
        Project('p-id').unpause_autopilot()
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilot/',
                      body='',
                      status=202,
                      content_type='application/json')
        self.assertTrue(Project('p-id').unpause_autopilot())
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'command': 'start',
        }))

    @responses.activate
    def test_start_autopilot(self):
        """
        Project('p-id').start_autopilot('featurelist-id')
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilots/',
                      body='',
                      status=201,
                      content_type='application/json')
        Project('p-id').start_autopilot('featurelist-id')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'featurelistId': 'featurelist-id',
            'mode': AUTOPILOT_MODE.FULL_AUTO
        }))

    @responses.activate
    def test_get_featurelists(self):
        """project.get_featurelists()

        """
        some_featurelists = [
            {'_id': 'f-id-1',
             'pid': 'p-id',
             'name': 'Raw Features',
             'features': ['One Fish', 'Two Fish', 'Red Fish', 'Blue Fish']},
            {'_id': 'f-id-2',
             'pid': 'p-id',
             'name': 'Informative Features',
             'features': ['One Fish', 'Red Fish', 'Blue Fish']},
            {'_id': 'f-id-3',
             'pid': 'p-id',
             'name': 'Custom Features',
             'features': ['One Fish', 'Blue Fish']},
        ]

        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/featurelists/',
                      body=json.dumps(some_featurelists),
                      status=200,
                      content_type='application/json')
        flists = Project('p-id').get_featurelists()
        for flist in flists:
            self.assertIsInstance(flist, Featurelist)

    @responses.activate
    def test_create_featurelist(self):
        """Project.create_featurelist(name='Featurelist Name',
                                      features=list_of_features)

        """
        project = Project('p-id')
        name = 'Featurelist name'
        features = ['One Fish', 'Two Fish', 'Blue Fish']

        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/featurelists/',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={
                          'Location': 'https://host_name.com/projects/p-id/featurelists/f-id-new/'
                      })
        new_flist = project.create_featurelist(name, features)
        self.assertEqual(new_flist.name, name)
        self.assertEqual(new_flist.features, features)
        self.assertEqual(new_flist.project.id, 'p-id')

    def test_create_featurelist_duplicate_features(self):
        project = Project('p-id')
        with self.assertRaisesRegexp(
            errors.DuplicateFeaturesError,
            "Can't create featurelist with duplicate features"
        ):
            project.create_featurelist('test', ['feature', 'feature'])

    @responses.activate
    def test_start_project(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric")
        """
        path = fixture_file_path('synthetic-100.csv')
        self.prep_successful_project_creation_responses(project_id='p-id')

        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')

        self.prep_successful_aim_responses(project_id='p-id',
                                           project_info=AIMED_PROJECT_JSON)

        proj = Project.start(project_name="test_name",
                             sourcedata=path,
                             target="a_target",
                             worker_count=4,
                             metric="a_metric")
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

    @responses.activate
    def test_start_project_from_dataframe(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric")
        """
        self.prep_successful_project_creation_responses(project_id='p-id')

        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')

        self.prep_successful_aim_responses(project_id='p-id')

        dataframe = pd.DataFrame({'a_target': range(100),
                                  'predictor': range(100, 200)})
        proj = Project.start(dataframe,
                             "a_target",
                             "test_name",
                             worker_count=4,
                             metric="a_metric")
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

    @responses.activate
    def test_start_project_in_manual_mode(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric",
                      autopilot_on=False)
        """
        path = fixture_file_path('synthetic-100.csv')
        self.prep_successful_project_creation_responses(project_id='p-id')
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        self.prep_successful_aim_responses(project_id='p-id')

        proj = Project.start(path,
                             "test_name",
                             "a_target",
                             worker_count=4,
                             metric="a_metric",
                             autopilot_on=False)
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

        req_body = json.loads(responses.calls[4].request.body)
        self.assertEqual(req_body['mode'], AUTOPILOT_MODE.MANUAL)

    def assert_project_start_call_order(self):
        """Run this assertion to assert that the expected calls for project.start
        happened, and in the correct order

        This is a terribly brittle test. If we can come up with something
        better, let's go with that.
        """
        # Create Project
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/')
        self.assertEqual(responses.calls[0].request.method, 'POST')

        # Get Project Creation Status
        self.assertEqual(responses.calls[1].request.url,
                         'https://host_name.com/status/status-id/')
        self.assertEqual(responses.calls[1].request.method, 'GET')

        # Get Created Project
        self.assertEqual(responses.calls[2].request.url,
                         'https://host_name.com/projects/p-id/')
        self.assertEqual(responses.calls[2].request.method, 'GET')

        # Set Worker Count
        self.assertEqual(responses.calls[3].request.url,
                         'https://host_name.com/projects/p-id/')
        self.assertEqual(responses.calls[3].request.method, 'PATCH')

        # Set Target
        self.assertEqual(responses.calls[4].request.url,
                         'https://host_name.com/projects/p-id/aim/')
        self.assertEqual(responses.calls[4].request.method, 'PATCH')

        # Get Status of Finalizing Project
        self.assertEqual(responses.calls[5].request.url,
                         'https://host_name.com/status/some-status/')
        self.assertEqual(responses.calls[5].request.method, 'GET')

        # Get Finalized Project
        self.assertEqual(responses.calls[6].request.url,
                         'https://host_name.com/projects/p-id/')
        self.assertEqual(responses.calls[6].request.method, 'GET')

    @responses.activate
    def test_set_target_featurelist(self):
        """
        proj.set_target('test_target', featurelist_id=...)
        """
        self.prep_successful_aim_responses(project_id='p-id')
        Project('p-id').set_target('a_target', featurelist_id='f-id-3')
        body = json.loads(responses.calls[0].request.body)
        assert body['featurelistId'] == 'f-id-3'

    @responses.activate
    def test_attach_file_with_link_goes_to_url(self):
        """
        Project.create('https://google.com/file.csv')
        """
        self.prep_successful_project_creation_responses()

        link = 'http:/google.com/datarobot.csv'
        Project.create(link)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({"url": link, "projectName": "Untitled Project"}))
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')

    @responses.activate
    def test_attach_file_with_file_path(self):
        """
        Project.create('synthetic-100.csv')
        """
        self.prep_successful_project_creation_responses()

        path = fixture_file_path('synthetic-100.csv')
        Project.create(path)

        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message.read())

    @responses.activate
    def test_attach_file_with_non_csv_file_path(self):
        """
        Project.create('dataset.xlsx')
        """
        self.prep_successful_project_creation_responses()

        path = fixture_file_path('onehundredrows.xlsx')
        Project.create(path)
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body.read()
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message)
        fname = re.search(b'filename="(.*)"',
                          request_message).group(1)
        self.assertEqual(fname, b'onehundredrows.xlsx')

    @responses.activate
    def test_get_status_underscorizes(self):
        body = json.dumps({'autopilotDone': True,
                           'stage': 'modeling',
                           'stageDescription': 'Ready for modeling'})
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/status/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        status = Project('p-id').get_status()
        self.assertEqual(status['stage'], 'modeling')
        self.assertTrue(status['autopilot_done'])

    @responses.activate
    def test_get_blueprints(self):
        body = json.dumps([
            {"projectId": "p-id",
             "processes": [
                 "Regularized Linear Model Preprocessing v5",
                 "Log Transformed Response"
             ],
             "id": "cbb4d6101dea1768ed79d75edd84c6c7",
             "modelType": "Auto-tuned K-Nearest Neighbors Regressor (Minkowski Distance)"
             },
            {"projectId": "p-id",
             "processes": [
                 "Regularized Linear Model Preprocessing v12",
                 "Log Transformed Response"
             ],
             "id": "e0708bd47f9fd21019a5ab7846e8364d",
             "modelType": "Auto-tuned Stochastic Gradient Descent Regression"
             }])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/blueprints/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        menu = Project('p-id').get_blueprints()
        for item in menu:
            self.assertIsInstance(item, Blueprint)
            self.assertEqual(item.project_id, 'p-id')
        bluepr1 = menu[0]
        bluepr2 = menu[1]
        self.assertIsInstance(bluepr1.processes, list)
        self.assertEqual(bluepr1.processes[0],
                         'Regularized Linear Model Preprocessing v5')
        self.assertEqual(bluepr1.processes[1], 'Log Transformed Response')
        self.assertEqual(bluepr1.model_type,
                         'Auto-tuned K-Nearest Neighbors Regressor (Minkowski Distance)')
        self.assertIsInstance(bluepr2.processes, list)
        self.assertEqual(bluepr2.processes[0],
                         'Regularized Linear Model Preprocessing v12')
        self.assertEqual(bluepr2.processes[1],
                         'Log Transformed Response')
        self.assertEqual(bluepr2.model_type,
                         'Auto-tuned Stochastic Gradient Descent Regression')


class TestProjectJobListing(SDKTestcase):

    job1_queued_dict = {
                'status': 'queue',
                'processes': [
                    'Majority Class Classifier'
                ],
                'projectId': '556902e8100d2b3728d47551',
                'samplePct': 32.0,
                'modelType': 'Majority Class Classifier',
                'featurelistId': '556902eb100d2b37d1130771',
                'blueprintId': '89e08076a908e859c07af49bd4aa6a0f',
                'id': '10',
                'modelId': '556902ef100d2b37da13077c'
            }
    job2_queued_dict = {
                'status': 'queue',
                'processes': [
                    'One-Hot Encoding',
                    'Missing Values Imputed',
                    'RuleFit Classifier'
                ],
                'projectId': '556902e8100d2b3728d47551',
                'samplePct': 32.0,
                'modelType': 'RuleFit Classifier',
                'featurelistId': '556902eb100d2b37d1130771',
                'blueprintId': 'a8959bc1d46f07fb3dc14db7c1e3fc99',
                'id': '11',
                'modelId': '556902ef100d2b37da13077d'
            }
    job3_queued_dict = {
                'status': 'queue',
                'processes': [
                    'One-Hot Encoding',
                    'Missing Values Imputed',
                    'RuleFit Classifier'
                ],
                'projectId': '556902e8100d2b3728d47551',
                'samplePct': 64.0,
                'modelType': 'RuleFit Classifier',
                'featurelistId': '556902eb100d2b37d1130771',
                'blueprintId': 'a8959bc1d46f07fb3dc14db7c1e3fc99',
                'id': '17',
                'modelId': '556902ef100d2b37da13077d'
            }
    job1_inprogress_dict = dict(job1_queued_dict, status='inprogress')
    job2_inprogress_dict = dict(job2_queued_dict, status='inprogress')

    predict_job_queued_dict = {
        'status': 'queue',
        'projectId': '56b62892ccf94e7e939c89c8',
        'message': '',
        'id': '27',
        'modelId': '56b628b7ccf94e0444bb8152'
    }

    predict_job_errored_dict = {
        'status': 'error',
        'projectId': '56b62892ccf94e7e939c89c8',
        'message': '',
        'id': '23',
        'modelId': '56b628b7ccf94e0444bb8152'
    }

    all_jobs_response = {
        'count': 4,
        'next': None,
        'jobs': [
            {
                'status': 'inprogress',
                'url': 'https://host_name.com/projects/p-id/modelJobs/1/',
                'id': '1',
                'jobType': 'model',
                'projectId': 'p-id'
            },
            {
                'status': 'inprogress',
                'url': 'https://host_name.com/projects/p-id/modelJobs/2/',
                'id': '2',
                'jobType': 'model',
                'projectId': 'p-id'
            },
            {
                'status': 'queue',
                'url': 'https://host_name.com/projects/p-id/predictJobs/3/',
                'id': '3',
                'jobType': 'predict',
                'projectId': 'p-id'
            },
            {
                'status': 'queue',
                'url': 'https://host_name.com/projects/p-id/modelJobs/4/',
                'id': '4',
                'jobType': 'model',
                'projectId': 'p-id'
            }
        ],
        'previous': None
    }

    all_error_jobs_response = {
        'count': 1,
        'next': None,
        'jobs': [
            {
                'status': 'error',
                'url': 'https://host_name.com/projects/p-id/predictJobs/3/',
                'id': '3',
                'jobType': 'predict',
                'projectId': 'p-id'
            }
        ],
        'previous': None
    }

    @responses.activate
    def test_get_all_jobs(self):
        body = json.dumps(self.all_jobs_response)
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/jobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_all_jobs()
        self.assertEqual(len(jobs), 4)

    @responses.activate
    def test_get_all_errored_jobs(self):
        body = json.dumps(self.all_error_jobs_response)
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/jobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_all_jobs(status=QUEUE_STATUS.ERROR)
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/p-id/jobs/?status=error')
        self.assertEqual(len(jobs), 1)

    @responses.activate
    def test_get_model_jobs(self):
        job_dict = self.job1_queued_dict
        body = json.dumps([job_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/modelJobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_model_jobs(status=QUEUE_STATUS.QUEUE)
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/modelJobs/?status=queue')
        self.assertEqual(len(jobs), 1)
        self.assertDictEqual(jobs[0].__dict__, ModelJob(job_dict).__dict__)

    @responses.activate
    def test_get_model_jobs_requests_all_by_default(self):
        job_dict = self.job1_queued_dict
        body = json.dumps([job_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/modelJobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_model_jobs()
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/modelJobs/')
        self.assertEqual(len(jobs), 1)
        self.assertDictEqual(jobs[0].__dict__, ModelJob(job_dict).__dict__)

    @responses.activate
    def test_get_predict_jobs(self):
        body = json.dumps([self.predict_job_errored_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/predictJobs/',
                      status=200,
                      body=body,
                      content_type='application/json')
        jobs = Project('p-id').get_predict_jobs(status=QUEUE_STATUS.ERROR)
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/p-id/predictJobs/?status=error')
        self.assertEqual(len(jobs), 1)
        result_job = jobs[0]
        expected_job = PredictJob(self.predict_job_errored_dict)
        self.assertEqual(expected_job.id, result_job.id)
        self.assertEqual(expected_job.project, result_job.project)

    @responses.activate
    def test_get_predict_jobs_default(self):
        body = json.dumps([self.predict_job_queued_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/predictJobs/',
                      status=200,
                      body=body,
                      content_type='application/json')
        jobs = Project('p-id').get_predict_jobs()
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/p-id/predictJobs/')
        self.assertEqual(len(jobs), 1)
        result_job = jobs[0]
        expected_job = PredictJob(self.predict_job_queued_dict)
        self.assertEqual(expected_job.id, result_job.id)
        self.assertEqual(expected_job.project, result_job.project)

    @patch('datarobot.Project.get_model_jobs')
    def test_job_status_counter(self, mock_get_jobs):
        project = Project('p-id')
        jobs0 = []
        jobs1 = [ModelJob(self.job1_queued_dict)]
        jobs2 = [ModelJob(self.job1_inprogress_dict), ModelJob(self.job2_queued_dict)]
        jobs3 = [ModelJob(self.job2_inprogress_dict)]
        mock_get_jobs.side_effect = [jobs0, jobs1, jobs2, jobs3]
        assert project._get_job_status_counts() == (0, 0)
        assert project._get_job_status_counts() == (0, 1)
        assert project._get_job_status_counts() == (1, 1)
        assert project._get_job_status_counts() == (1, 0)

    @patch('datarobot.Project.get_status')
    def test_wait_for_autopilot(self, mock_get_status):
        def make_status(autopilot_done):
            return {'autopilot_done': autopilot_done}
        mock_get_status.side_effect = [make_status(False)]*3 + \
                                      [make_status(True)] + \
                                      [make_status(False)]
        project = Project('p-id')
        project.wait_for_autopilot(check_interval=.5, verbosity=0)
        assert mock_get_status.call_count == 4

    @patch('datarobot.Project.get_status')
    def test_wait_for_autopilot_timeout(self, mock_get_status):
        project = Project('p-id')
        mock_get_status.return_value = {'autopilot_done': False}
        self.assertRaises(errors.AsyncTimeoutError,
                          project.wait_for_autopilot,
                          check_interval=10, verbosity=0, timeout=.2)


class TestProjectList(SDKTestcase):

    def setUp(self):
        self.raw_return = """
        [
            {
            "project_name": "Api project",
            "_id": "54c627fa100d2b2c7002a489"
            },
            {
            "_id": "54c78125100d2b2fe3b296b6",
            "project_name": "Untitled project"
            }
        ]
        """

    @responses.activate
    def test_list_projects(self):
        """
        Test list projects
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/',
                      body=self.raw_return,
                      status=200,
                      content_type='application/json')
        project_lists = Project.list()
        self.assertIsInstance(project_lists, list)
        self.assertEquals(project_lists[0].id, '54c627fa100d2b2c7002a489')
        self.assertEquals(project_lists[0].project_name, 'Api project')
        self.assertEquals(project_lists[1].id, '54c78125100d2b2fe3b296b6')
        self.assertEquals(project_lists[1].project_name, 'Untitled project')

    @responses.activate
    def test_with_manual_search_params(self):
        responses.add(responses.GET,
                      'https://host_name.com/projects/?projectName=x',
                      body=self.raw_return,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)
        Project('p-id').list(search_params={'project_name': 'x'})
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/?projectName=x')

    @responses.activate
    def test_with_bad_search_params(self):
        with self.assertRaises(TypeError):
            Project('p-id').list(search_params=12)


class TestGetModels(SDKTestcase, URLParamsTestCase):

    def setUp(self):
        super(TestGetModels, self).setUp()
        self.raw_data = """
        [
    {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9657"
},
    {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9658"
}
]
        """

    @responses.activate
    def test_get_models_ordered_by_metric_by_default(self):
        """
        Project('p-id').get_models()
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/models/?orderBy=-metric',
                      body=self.raw_data,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)
        leaderboard = Project('p-id').get_models()
        self.assertNotEqual(0, len(leaderboard))
        for item in leaderboard:
            self.assertIsInstance(item, Model)
        self.assertEqual(leaderboard[0].id, '556ce973100d2b6e51ca9657')
        self.assertEqual(leaderboard[1].id, '556ce973100d2b6e51ca9658')
        self.assertEqual(leaderboard[0].project.id, 'p-id')
        self.assertIsInstance(leaderboard[1].project, Project)
        self.assertEqual(leaderboard[1].project.id, 'p-id')

    @responses.activate
    def test_get_models_ordered_by_specific_field(self):
        # ordering
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/models/?orderBy=samplePct',
                      body=self.raw_data,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)
        Project('p-id').get_models(order_by='samplePct')
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/?orderBy=samplePct')

    @responses.activate
    def test_get_models_orderd_by_two_fields(self):
        # ordering by two fields
        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/models/?orderBy=samplePct%2C-metric',
            body=self.raw_data,
            status=200,
            content_type='application/json',
            match_querystring=True)
        Project('p-id').get_models(
            order_by=['sample_pct', '-metric'])
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/?orderBy=samplePct%2C-metric')

    @responses.activate
    def test_get_models_two_order_fields_and_filtering(self):
        # ordering by two fields plus filtering
        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/models/'
            '?withMetric=RMSE&orderBy=metric%2C-samplePct',
            body=self.raw_data,
            status=200,
            content_type='application/json',
            match_querystring=True)
        Project('p-id').get_models(
            order_by=['metric', '-sample_pct'], with_metric='RMSE')

    def test_order_by_with_unexpected_param_fails(self):
        with self.assertRaisesRegexp(ValueError, 'Provided order_by attribute'):
            Project('p-id').get_models(order_by='someThing')

    def test_order_by_with_bad_param_fails(self):
        with self.assertRaisesRegexp(TypeError, 'Provided order_by attribute'):
            Project('p-id').get_models(order_by=True)

    def test_with_bad_search_param_fails(self):
        with self.assertRaises(TypeError):
            Project('p-id').get_models(search_params=True)

    def _canonize_order_by_handles_none(self):
        proj = Project('p-id')
        self.assertIsNone(proj._canonize_order_by(None))
