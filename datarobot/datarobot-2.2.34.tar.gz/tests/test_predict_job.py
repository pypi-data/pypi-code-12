import json
import unittest

import mock
import responses
import pandas as pd

from datarobot import errors, Job, PredictJob, Project
from datarobot.utils import raw_prediction_response_to_dataframe
from datarobot.models.predict_job import (
    wait_for_async_predictions,
)
from .utils import SDKTestcase


SAMPLE_PREDICTION_RETURN = json.dumps({
    u'positiveClass': 1.0,
    u'task': u'Binary',
    u'predictions': [
        {u'positiveProbability': 0.9, u'prediction': 1.0,
         u'rowId': 0},
        {u'positiveProbability': 0.1, u'prediction': 0.0,
         u'rowId': 1},
        {u'positiveProbability': 0.8, u'prediction': 1.0,
         u'rowId': 2}
    ]
})

SAMPLE_REGRESSION_PREDICTION_RETURN = json.dumps({
    u'positiveClass': None,
    u'task': u'Regression',
    u'predictions': [
        {u'positiveProbability': None, u'prediction': 32.0,
         u'rowId': 0},
        {u'positiveProbability': None, u'prediction': 100.0,
         u'rowId': 1},
        {u'positiveProbability': None, u'prediction': 212.0,
         u'rowId': 2}
    ]
})


class TestPredictJob(SDKTestcase):

    def setUp(self):
        super(TestPredictJob, self).setUp()
        self.project_id = '556902e8100d2b3728d47551'
        self.model_id = '556902ef100d2b37da13077d'
        self.predict_job_id = 111
        self.post_url = 'https://host_name.com/projects/{}/predictions/'.format(
            self.project_id)
        self.get_job_url = 'https://host_name.com/projects/{}/predictJobs/{}/'.format(
            self.project_id,
            self.predict_job_id
        )
        self.get_predictions_url = (
            'https://host_name.com/projects/{}/predictions/123/'.format(
                self.project_id
            )
        )
        self.predict_job_data = {
            'status': 'queue',
            'id': self.predict_job_id,
            'projectId': self.project_id,
            'modelId': self.model_id,
        }

        self.predict_job_with_message = {
            'status': 'error',
            'id': self.predict_job_id,
            'projectId': self.project_id,
            'modelId': self.model_id,
            'message': 'Clearly this is user error :)'
        }

        self.mock_generic_job_data = {
            'status': 'inprogress',
            'url': 'https://host_name.com/projects/{}/predictJobs/1/'.format(self.project_id),
            'id': '1',
            'jobType': 'predict',
            'projectId': self.project_id
        }

        self.mock_model_job_data = {
            'status': 'inprogress',
            'url': 'https://host_name.com/projects/{}/modelJobs/2/'.format(self.project_id),
            'id': '2',
            'jobType': 'model',
            'projectId': self.project_id
        }

    def test_instantiate_predict_job(self):
        job = PredictJob(self.predict_job_data)
        print(job)  # checks that method relevant to print works on this (failed in one release)
        self.assertEqual(job.id, self.predict_job_id)
        self.assertEqual(job.status, 'queue')
        self.assertIsInstance(job.project, Project)
        self.assertEqual(job.project.id, '556902e8100d2b3728d47551')

        with self.assertRaises(ValueError):
            PredictJob('qid')

    @responses.activate
    def test_from_job(self):
        responses.add(
            responses.GET,
            'https://host_name.com/projects/{}/predictJobs/1/'.format(self.project_id),
            status=200,
            body=json.dumps(self.predict_job_with_message),
            content_type='application/json'
        )
        generic_job = Job(self.mock_generic_job_data)
        predict_job = PredictJob.from_job(generic_job)

        self.assertEqual(predict_job.status, 'error')
        self.assertEqual(predict_job.job_type, 'predict')
        self.assertEqual(predict_job.project, Project(self.project_id))
        self.assertEqual(predict_job.model.id, self.model_id)

    def test_from_job_wrong_type(self):
        generic_job = Job(self.mock_model_job_data)
        with self.assertRaises(ValueError):
            PredictJob.from_job(generic_job)

    @mock.patch('os.path.isfile')
    def test_create_non_ascii_filename(self, isfile_mock):
        isfile_mock.return_value = True
        bad_filename = u'\xc3\x98.csv'
        with self.assertRaises(errors.IllegalFileName):
            PredictJob.create(mock.Mock(), sourcedata=bad_filename)

    def test_create_bad_sourcedata(self):
        with self.assertRaisesRegexp(
            errors.InputNotUnderstoodError,
            'sourcedata parameter not understood.'
        ):
            PredictJob.create(mock.Mock(), sourcedata=123)

    @responses.activate
    def test_create_success(self):
        model = mock.Mock()
        model.id = self.model_id
        model.project.id = self.project_id
        responses.add(
            responses.POST,
            self.post_url,
            status=202,
            body='',
            adding_headers={'Location': 'https://host_name.com' + self.get_job_url}
        )
        predict_job_id = PredictJob.create(model, b'one,two\n3,4')
        self.assertEqual(predict_job_id, str(self.predict_job_id))

    @responses.activate
    def test_cancel(self):
        predict_job = PredictJob(self.predict_job_data)
        responses.add(responses.DELETE, self.get_job_url,
                      status=204, body='', content_type='application/json')
        predict_job.cancel()
        self.assertEqual(responses.calls[0].request.method, 'DELETE')

    @responses.activate
    def test_get_unfinished_predict_job_with_message(self):
        """A new attribute of PredictJob beginning in DataRobot API v2.1"""
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.predict_job_with_message),
            content_type='application/json'
        )
        predict_job = PredictJob.get(self.project_id, self.predict_job_id)
        self.assertIsInstance(predict_job, PredictJob)
        self.assertEqual(predict_job.id, self.predict_job_id)
        self.assertEqual(predict_job.status, 'error')
        self.assertEqual(predict_job.message, 'Clearly this is user error :)')

    @responses.activate
    def test_get_unfinished_predict_job(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.predict_job_data),
            content_type='application/json'
        )
        predict_job = PredictJob.get(self.project_id, self.predict_job_id)
        self.assertIsInstance(predict_job, PredictJob)
        self.assertEqual(predict_job.id, self.predict_job_id)
        self.assertEqual(predict_job.status, 'queue')
        self.assertEqual(predict_job.message, '')

    @responses.activate
    def test_get_finished_predict_job(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=303,
            body='',
        )
        with self.assertRaises(errors.PendingJobFinished):
            PredictJob.get(self.project_id, self.predict_job_id)

    @responses.activate
    def test_get_predict_job_async_failure(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=202,
            body='',
        )
        with self.assertRaisesRegexp(
            errors.AsyncFailureError,
            'Server unexpectedly returned status code 202'
        ):
            PredictJob.get(self.project_id, self.predict_job_id)

    @responses.activate
    def test_get_unfinished_predictions(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(self.predict_job_data),
            content_type='application/json'
        )
        with self.assertRaisesRegexp(
            errors.JobNotFinished,
            'Pending job status is queue'
        ):
            PredictJob.get_predictions(self.project_id, self.predict_job_id)

    @responses.activate
    def test_get_predictions_async_failure(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=202,
            body='',
        )
        with self.assertRaisesRegexp(
            errors.AsyncFailureError,
            'Server unexpectedly returned status code 202'
        ):
            PredictJob.get_predictions(self.project_id, self.predict_job_id)

    @responses.activate
    def test_get_finished_predictions(self):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=303,
            body='',
            adding_headers={'Location': self.get_predictions_url}
        )
        responses.add(
            responses.GET,
            self.get_predictions_url,
            status=200,
            body=SAMPLE_PREDICTION_RETURN,
            content_type='application/json'
        )
        predictions = PredictJob.get_predictions(self.project_id, self.predict_job_id)
        self.assertIsInstance(predictions, pd.DataFrame)
        self.assertEqual(predictions.shape, (3, 3))
        self.assertEqual(
            sorted(predictions.columns),
            ['positive_probability', 'prediction', 'row_id'],
        )


class TestWaitForAsyncPredictions(SDKTestcase):
    def setUp(self):
        super(TestWaitForAsyncPredictions, self).setUp()
        self.pid = 'p-id'
        self.predict_job_id = '5'
        self.get_job_url = 'https://host_name.com/projects/{}/predictJobs/{}/'.format(
            self.pid,
            self.predict_job_id,
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
            'Predictions generation timed out in'
        ):
            wait_for_async_predictions(self.pid, self.predict_job_id, max_wait=1)

    @responses.activate
    @mock.patch('datarobot.models.predict_job.PredictJob.get_predictions')
    def test_success(self, get_predictions):
        responses.add(
            responses.GET,
            self.get_job_url,
            status=303,
            body='',
            content_type='application/json'
        )
        wait_for_async_predictions(self.pid, self.predict_job_id)
        self.assertEqual(get_predictions.call_count, 1)

    @responses.activate
    @mock.patch('datarobot.models.predict_job.PredictJob.get_predictions')
    def test_error(self, get_predictions):
        data = {'status': 'error'}
        responses.add(
            responses.GET,
            self.get_job_url,
            status=200,
            body=json.dumps(data),
            content_type='application/json'
        )
        with self.assertRaisesRegexp(
            errors.AsyncPredictionsGenerationError,
            'Predictions generation unsuccessful',
        ):
            wait_for_async_predictions(self.pid, self.predict_job_id)


class TestRawPredictionResponseToDataframe(unittest.TestCase):
    def test_parse_regression_predictions(self):
        data = json.loads(SAMPLE_REGRESSION_PREDICTION_RETURN)

        frame = raw_prediction_response_to_dataframe(data)
        self.assertEqual(frame.shape, (3, 2))
        self.assertEqual(
            sorted(frame.columns),
            ['prediction', 'row_id'],
        )

    def test_parse_classification_predictions(self):
        data = json.loads(SAMPLE_PREDICTION_RETURN)
        frame = raw_prediction_response_to_dataframe(data)
        self.assertEqual(frame.shape, (3, 3))
        self.assertEqual(
            sorted(frame.columns),
            ['positive_probability', 'prediction', 'row_id'],
        )
