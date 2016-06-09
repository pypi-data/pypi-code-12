import json

import mock
import responses
from datarobot import Job, ModelJob, Project, Blueprint, errors
from datarobot.models.modeljob import wait_for_async_model_creation
from .utils import SDKTestcase


fully_trained_model = """
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
    "id": "l-id"
}
"""


class TestWaitForAsyncModelCreation(SDKTestcase):
    def setUp(self):
        super(TestWaitForAsyncModelCreation, self).setUp()
        self.pid = 'p-id'
        self.model_job_id = '5'
        self.get_job_url = 'https://host_name.com/projects/{}/modelJobs/{}/'.format(
            self.pid,
            self.model_job_id,
        )

    @responses.activate
    def test_timeout(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps({}),
            content_type='application/json'
        )
        with self.assertRaisesRegexp(
            errors.AsyncTimeoutError,
            'Model creation timed out in'
        ):
            wait_for_async_model_creation(
                self.pid, self.model_job_id, max_wait=1)

    @responses.activate
    @mock.patch('datarobot.models.modeljob.ModelJob.get_model')
    def test_success(self, get_model):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=303,
            body='',
            content_type='application/json'
        )
        wait_for_async_model_creation(self.pid, self.model_job_id)
        self.assertEqual(get_model.call_count, 1)

    @responses.activate
    @mock.patch('datarobot.models.modeljob.ModelJob.get_model')
    def test_error(self, get_model):
        data = {'status': 'error'}
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(data),
            content_type='application/json'
        )
        with self.assertRaisesRegexp(
            errors.AsyncModelCreationError,
            "Model creation unsuccessful",
        ):
            wait_for_async_model_creation(self.pid, self.model_job_id)


class TestJobModel(SDKTestcase):
    mock_generic_job_data = {
        'status': 'inprogress',
        'url': 'https://host_name.com/projects/p-id/modelJobs/1/',
        'id': '1',
        'jobType': 'model',
        'projectId': 'p-id'
    }

    mock_model_job_data = {
        'status': 'inprogress',
        'processes': [
            'One-Hot Encoding',
            'Bernoulli Naive Bayes classifier (scikit-learn)',
            'Missing Values Imputed',
            'Gaussian Naive Bayes classifier (scikit-learn)',
            'Naive Bayes combiner classifier',
            'Calibrate predictions'
        ],
        'projectId': 'p-id',
        'samplePct': 28.349,
        'modelType': 'Naive Bayes combiner classifier',
        'featurelistId': '56d8620bccf94e26f37af0a3',
        'modelCategory': 'model',
        'blueprintId': '2a1b9ae97fe61880332e196c770c1f9f',
        'id': '1'
    }

    mock_predict_job_data = {
        'status': 'error',
        'url': 'https://host_name.com/projects/p-id/predictJobs/64/',
        'id': '64',
        'jobType': 'predict',
        'projectId': 'p-id'
    }

    def test_instantiate_job(self):
        data = {
            "status": "queue",
            "processes": [
                "One-Hot Encoding",
                "Missing Values Imputed",
                "RuleFit Classifier"
            ],
            "projectId": "556902e8100d2b3728d47551",
            "samplePct": 64,
            "modelType": "RuleFit Classifier",
            "featurelistId": "556902eb100d2b37d1130771",
            "blueprintId": "a8959bc1d46f07fb3dc14db7c1e3fc99",
            "id": 11,
            "modelId": "556902ef100d2b37da13077d"
        }
        job = ModelJob(data)
        self.assertEqual(job.status, 'queue')
        self.assertEqual(job.job_type, 'model')
        self.assertEqual(job.processes, data['processes'])
        self.assertEqual(job.sample_pct, 64)
        self.assertEqual(job.model_type, "RuleFit Classifier")
        self.assertIsInstance(job.project, Project)
        self.assertEqual(job.project.id, "556902e8100d2b3728d47551")
        self.assertIsInstance(job.blueprint, Blueprint)
        self.assertEqual(job.blueprint.id, "a8959bc1d46f07fb3dc14db7c1e3fc99")

        repr(job)

        with self.assertRaises(ValueError):
            ModelJob('qid')

    @responses.activate
    def test_from_job(self):
        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/modelJobs/1/',
            status=200,
            body=json.dumps(self.mock_model_job_data),
            content_type='application/json'
        )
        generic_job = Job(self.mock_generic_job_data)
        model_job = ModelJob.from_job(generic_job)

        self.assertEqual(model_job.status, 'inprogress')
        self.assertEqual(model_job.job_type, 'model')
        self.assertEqual(model_job.project, Project('p-id'))
        self.assertEqual(model_job.processes, self.mock_model_job_data['processes'])

    def test_from_job_wrong_type(self):
        generic_job = Job(self.mock_predict_job_data)
        with self.assertRaises(ValueError):
            ModelJob.from_job(generic_job)

    @responses.activate
    def test_cancel(self):
        data = {'status': 'inprogress',
                'samplepct': 64.0,
                'processes': ['One-Hot Encoding',
                              'Missing Values Imputed',
                              'Standardize',
                              'Linear Regression'],
                'modelType': 'Linear Regression',
                'featurelistId': '55666d05100d2b01a1104dae',
                'blueprintId': '3bb4665320be633b30a9601b3e73284d',
                'projectId': '55666eb9100d2b109b59e267',
                'id': 5,
                'modelId': '55666d0d100d2b01b1104db4'}
        job = ModelJob(data)
        responses.add(responses.DELETE,
                      'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
                      status=204,
                      body='',
                      content_type='application/json'
                      )
        job.cancel()
        self.assertEqual(responses.calls[0].request.method, 'DELETE')

    @responses.activate
    def test_get_success(self):
        data = {'status': 'inprogress',
                'samplepct': 64.0,
                'processes': ['One-Hot Encoding',
                              'Missing Values Imputed',
                              'Standardize',
                              'Linear Regression'],
                'modelType': 'Linear Regression',
                'featurelistId': '55666d05100d2b01a1104dae',
                'blueprintId': '3bb4665320be633b30a9601b3e73284d',
                'projectId': '55666eb9100d2b109b59e267',
                'id': 5,
                'modelId': '55666d0d100d2b01b1104db4'}
        responses.add(responses.GET,
                      'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
                      status=200,
                      body=json.dumps(data),
                      content_type='application/json'
                      )
        job = ModelJob.get('55666eb9100d2b109b59e267', 5)
        self.assertEqual(responses.calls[0].request.method, 'GET')
        self.assertEqual(job.status, 'inprogress')

    @responses.activate
    def test_get_redirect(self):
        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            content_type='application/json',
            status=303,
            body='',
            adding_headers={'Location': 'http://pam/api/v2/projects/p-id/models/id/'}
        )
        with self.assertRaises(errors.PendingJobFinished):
            ModelJob.get('55666eb9100d2b109b59e267', 5)

    @responses.activate
    def test_get_exceptional(self):
        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            status=404,
            body=''
        )
        with self.assertRaises(errors.AppPlatformError):
            ModelJob.get('55666eb9100d2b109b59e267', 5)

    @responses.activate
    def test_get_unexpected_status_code(self):
        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            status=202,
            body=''
        )
        with self.assertRaisesRegexp(
                errors.AsyncFailureError,
                "Server unexpectedly returned status code"):
            ModelJob.get('55666eb9100d2b109b59e267', 5)

    @responses.activate
    def test_get_model_success(self):
        final_model_location = ('https://host_name.com/projects/55666eb9100d2b109b59e267/'
                                'models/5223deadbeefdeadbeef1234/')

        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            status=303,
            body='',
            adding_headers={'Location': final_model_location}
        )
        responses.add(
            responses.GET,
            final_model_location,
            status=200,
            body=fully_trained_model
        )
        ModelJob.get_model('55666eb9100d2b109b59e267', 5)

    @responses.activate
    def test_get_model_not_finished(self):
        model_job_data = {
            'status': 'queue',
            'processes': [
                'One-Hot Encoding',
                'Missing Values Imputed',
                'RuleFit Classifier'
            ],
            'projectId': '556902e8100d2b3728d47551',
            'samplePct': 64,
            'modelType': 'RuleFit Classifier',
            'featurelistId': '556902eb100d2b37d1130771',
            'blueprintId': 'a8959bc1d46f07fb3dc14db7c1e3fc99',
            'id': 5,
            'modelId': '556902ef100d2b37da13077d'
        }

        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            status=200,
            body=json.dumps(model_job_data)
        )
        with self.assertRaises(errors.JobNotFinished):
            ModelJob.get_model('55666eb9100d2b109b59e267', 5)

    @responses.activate
    def test_get_model_exceptional(self):
        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            status=404,
            body=''
        )
        with self.assertRaises(errors.AppPlatformError):
            ModelJob.get_model('55666eb9100d2b109b59e267', 5)

    @responses.activate
    def test_get_model_unexpected_status_code(self):
        final_model_location = ('https://host_name.com/projects/55666eb9100d2b109b59e267/'
                                'models/5223deadbeefdeadbeef1234/')

        responses.add(
            responses.GET,
            'https://host_name.com/projects/55666eb9100d2b109b59e267/modelJobs/5/',
            status=202,
            body='',
            adding_headers={'Location': final_model_location}
        )

        with self.assertRaisesRegexp(
                errors.AsyncFailureError,
                'Server unexpectedly returned status code'):
            ModelJob.get_model('55666eb9100d2b109b59e267', 5)
