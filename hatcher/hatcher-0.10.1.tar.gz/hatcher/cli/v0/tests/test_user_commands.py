import json
import textwrap

import responses
from click.testing import CliRunner

from hatcher.core.url_templates import URLS
from hatcher.testing import unittest
from hatcher.tests.common import MainTestingMixin
from hatcher.cli import main


class TestUserCommands(MainTestingMixin, unittest.TestCase):
    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev.invalid'
        self.args = ['-u', self.host, 'user', 'repositories']

    @responses.activate
    def test_list_available_repositories(self):
        # Given
        expected = [
            'acme/prod',
            'enthought/free',
            'enthought/commercial',
        ]
        expected_output = textwrap.dedent("""\
        Repository
        --------------------
        {0}
        """).format('\n'.join(expected))

        responses.add(
            responses.GET,
            '{host}{path}'.format(
                host=self.host,
                path=URLS.v0.user.repositories.format(),
            ),
            status=200,
            body=json.dumps({'repositories': expected}),
            content_type='application/json',
        )

        # When
        result = CliRunner().invoke(main.hatcher, args=self.args)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertTrue(request.url.endswith('?include_indexable=False'))

    @responses.activate
    def test_list_available_repositories_include_indexable(self):
        # Given
        expected = [
            'acme/prod',
            'enthought/free',
            'enthought/commercial',
            'enthought/gpl',
        ]
        expected_output = textwrap.dedent("""\
        Repository
        --------------------
        {0}
        """).format('\n'.join(expected))

        responses.add(
            responses.GET,
            '{host}{path}'.format(
                host=self.host,
                path=URLS.v0.user.repositories.format(),
            ),
            status=200,
            body=json.dumps({'repositories': expected}),
            content_type='application/json',
        )

        # When
        result = CliRunner().invoke(
            main.hatcher, args=self.args + ['--include-indexable'])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)
        self.assertEqual(len(responses.calls), 1)
        request = responses.calls[0].request
        self.assertTrue(request.url.endswith('?include_indexable=True'))
