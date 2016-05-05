import json

import responses

from datarobot import Job, Project


mock_job_data = {
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


def test_instantiate(client):
    new_job = Job(mock_job_data)
    assert new_job.id == 1
    assert new_job.project == Project('p-id')
    assert new_job.status == 'inprogress'
    assert new_job.job_type == 'model'
    assert new_job._path == 'projects/p-id/modelJobs/1/'


@responses.activate
def test_get_full_details(client):
    body = json.dumps(mock_model_job_data)
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/modelJobs/1/',
        status=200,
        body=body,
        content_type='application/json'
    )
    generic_job = Job(mock_job_data)
    model_job_dict = generic_job._get_full_details()
    assert model_job_dict == mock_model_job_data


@responses.activate
def test_cancel_job(client):
    responses.add(
        responses.DELETE,
        'https://host_name.com/projects/p-id/modelJobs/1/',
        status=204,
        body='',
        content_type='application/json'
    )
    generic_job = Job(mock_job_data)
    generic_job.cancel()
