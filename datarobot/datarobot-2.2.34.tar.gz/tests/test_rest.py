import json
import responses

from datarobot import Project, AppPlatformError
from .utils import SDKTestcase


class Test400LevelErrors(SDKTestcase):

    @responses.activate
    def test_401_error_message(self):
        """For whatever reason, the `requests` library completely ignores the
        body in a 401 error, so, here is our own message
        """
        responses.add(
            responses.GET,
            'https://host_name.com/projects/',
            status=401,
        )

        with self.assertRaisesRegexp(AppPlatformError,
                                     'not properly authenticated'):
            Project.list()

    @responses.activate
    def test_403_error_message(self):
        """Same deal here, the `requests` library completely ignores the
        body in a 403 error, so, here is our own message
        """
        responses.add(
            responses.GET,
            'https://host_name.com/projects/',
            status=403,
        )

        with self.assertRaisesRegexp(AppPlatformError,
                                     'permissions'):
            Project.list()

    @responses.activate
    def test_extracts_error_message(self):
        data = {'message': 'project p-id has been deleted'}
        responses.add(responses.GET, 'https://host_name.com/projects/p-id/models/',
                      status=422,
                      body=json.dumps(data),
                      content_type='application/json')

        with self.assertRaisesRegexp(AppPlatformError, 'project p-id has been deleted'):
            Project({'id': 'p-id'}).get_models()
