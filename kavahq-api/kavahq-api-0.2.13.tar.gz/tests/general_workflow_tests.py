# -*- coding: utf-8 -*-

import mock
import unittest2
import urlparse


class GeneralWorkflowTest(unittest2.TestCase):
    def setUp(self):
        super(GeneralWorkflowTest, self).setUp()

    @mock.patch('kavahq.api.requests')
    def test_projects(self, requests):
        from kavahq.api import KavaApi
        company_name = '42 coffee cups'
        api = KavaApi(
            username='user', password='password', company_name=company_name,
        )
        auth = ('user', 'password')
        project_slug = '42-jobs'
        project_api = api.projects.get(project_slug)

        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        requests.get.return_value = response_mock
        requests.post.return_value = response_mock

        project_api.response
        self.assertEqual(
            requests.get.call_args[0][0],
            urlparse.urljoin(api.base_url, 'project/%s/' % project_slug)
        )
        self.assertDictContainsSubset(
            {
                'project_slug': project_slug,
                'project': project_slug,
            },
            requests.get.call_args[1]['params'],
        )

        project_api.estimate.response
        self.assertEqual(
            requests.get.call_args[0][0],
            urlparse.urljoin(api.base_url, 'project/estimate/')
        )
        self.assertDictContainsSubset(
            {
                'project_slug': project_slug,
                'project': project_slug,
                'company': company_name,
            },
            requests.get.call_args[1]['params'],
        )

        project_api.properties.response
        self.assertEqual(
            requests.post.call_args[0][0],
            urlparse.urljoin(api.base_url, 'project/properties/')
        )
        self.assertDictContainsSubset(
            {
                'project_slug': project_slug,
                'project': project_slug,
                'company': company_name,
            },
            requests.post.call_args[1]['data'],
        )

        project_api.tickets.response
        self.assertEqual(
            requests.post.call_args[0][0],
            urlparse.urljoin(api.base_url, 'project/tickets/')
        )
        self.assertDictContainsSubset(
            {
                'project_slug': project_slug,
                'project': project_slug,
                'company': company_name,
            },
            requests.post.call_args[1]['data'],
        )

        api.projects.response
        requests.get.assert_called_with(
            urlparse.urljoin(api.base_url, 'project/'),
            params={},
            auth=auth,
        )

        api.kavauser.get('by_score', min_score=-999, company='42 Coffee Cups'
                         ).response
        self.assertEqual(
            requests.post.call_args[0][0],
            urlparse.urljoin(api.base_url, 'kavauser/by_score/')
        )
