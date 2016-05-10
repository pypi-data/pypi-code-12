from __future__ import absolute_import
import os
from subprocess import CalledProcessError

from mock import (
    MagicMock,
    patch,
)

from six import BytesIO

from .base import Base
from deployer.utils import (
    _check_call,
    _is_qualified_charm_url,
    DeploymentError,
    dict_merge,
    ErrorExit,
    get_qualified_charm_url,
    HTTPError,
    mkdir,
    URLError,
)


class UtilTests(Base):

    def test_relation_list_merge(self):
        self.assertEqual(
            dict_merge(
                {'relations': [['m1', 'x1']]},
                {'relations': [['m2', 'x2']]}),
            {'relations': [['m1', 'x1'], ['m2', 'x2']]})

    def test_no_rels_in_target(self):
        self.assertEqual(
            dict_merge(
                {'a': 1},
                {'relations': [['m1', 'x1'], ['m2', 'x2']]}),
            {'a': 1, 'relations': [['m1', 'x1'], ['m2', 'x2']]})

    @patch('subprocess.check_output')
    def test_check_call_fail_no_retry(self, check_output):
        _e = CalledProcessError(returncode=1, cmd=['fail'])
        check_output.side_effect = _e
        self.assertRaises(
            ErrorExit, _check_call, params=['fail'], log=MagicMock())

    @patch('time.sleep')
    @patch('subprocess.check_output')
    def test_check_call_fail_retry(self, check_output, sleep):
        _e = CalledProcessError(returncode=1, cmd=['fail'])
        check_output.side_effect = _e
        self.assertRaises(
            ErrorExit, _check_call, params=['fail'], log=MagicMock(),
            max_retry=3)
        # 1 failure + 3 retries
        self.assertEquals(len(check_output.call_args_list), 4)

    @patch('time.sleep')
    @patch('subprocess.check_output')
    def test_check_call_succeed_after_retry(self, check_output, sleep):
        # call succeeds after the 3rd try
        _e = CalledProcessError(returncode=1, cmd=['maybe_fail'])
        check_output.side_effect = [
            _e, _e, 'good', _e]
        output = _check_call(
            params=['maybe_fail'], log=MagicMock(), max_retry=3)
        self.assertEquals(output, 'good')
        # 1 failure + 3 retries
        self.assertEquals(len(check_output.call_args_list), 3)

    def test_check_call_uses_shell(self):
        cmd = 'echo "foo"'
        self.assertRaises(
            OSError, _check_call, params=[cmd], log=MagicMock())
        output = _check_call(params=[cmd], log=MagicMock(), shell=True)
        self.assertEqual(output, b"foo\n")


class TestMkdir(Base):

    def setUp(self):
        self.playground = self.mkdir()

    def test_create_dir(self):
        # A directory is correctly created.
        path = os.path.join(self.playground, 'foo')
        mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_intermediate_dirs(self):
        # All intermediate directories are created.
        path = os.path.join(self.playground, 'foo', 'bar', 'leaf')
        mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_expand_user(self):
        # The ~ construction is expanded.
        with patch('os.environ', {'HOME': self.playground}):
            mkdir('~/in/my/home')
        path = os.path.join(self.playground, 'in', 'my', 'home')
        self.assertTrue(os.path.isdir(path))

    def test_existing_dir(self):
        # The function exits without errors if the target directory exists.
        path = os.path.join(self.playground, 'foo')
        os.mkdir(path)
        mkdir(path)

    def test_existing_file(self):
        # An OSError is raised if a file already exists in the target path.
        path = os.path.join(self.playground, 'foo')
        with open(path, 'w'):
            with self.assertRaises(OSError):
                mkdir(path)

    def test_failure(self):
        # Errors are correctly re-raised.
        path = os.path.join(self.playground, 'foo')
        os.chmod(self.playground, 0000)
        self.addCleanup(os.chmod, self.playground, 0o700)
        with self.assertRaises(OSError):
            mkdir(os.path.join(path))
        self.assertFalse(os.path.exists(path))


class TestCharmRevisioning(Base):
    """Test the functions related to charm URL revisioning."""

    def test_is_qualified_false(self):
        url = "cs:precise/mysql"
        self.assertFalse(_is_qualified_charm_url(url))

    def test_is_qualified_1_digit(self):
        url = "cs:precise/mysql-2"
        self.assertTrue(_is_qualified_charm_url(url))

    def test_is_qualified_many_digits(self):
        url = "cs:precise/mysql-2014"
        self.assertTrue(_is_qualified_charm_url(url))

    def test_is_qualified_no_digits(self):
        url = "cs:precise/mysql-"
        self.assertFalse(_is_qualified_charm_url(url))

    def test_get_qualified_url(self):
        fake_json = b"""
          {"cs:precise/mysql":
            {"revision":333}
          }
        """

        def mocked_urlopen(url):
            return BytesIO(fake_json)

        path = 'deployer.utils.urlopen'
        with patch(path, mocked_urlopen):
            url = get_qualified_charm_url('cs:precise/mysql')
        self.assertEqual('cs:precise/mysql-333', url)

    def test_get_qualified_url_raise_exception_on_HTTPError(self):
        def mocked_urlopen(url):
            raise HTTPError(url, 404, 'Bad Earl', None, None)

        with patch('deployer.utils.urlopen', mocked_urlopen):
            with self.assertRaises(DeploymentError) as exc:
                get_qualified_charm_url('cs:precise/mysql')
            expected = (
                'HTTP Error 404: '
                'Bad Earl (https://api.jujucharms.com/charmstore/charm-info'
                '?charms=cs:precise/mysql)')
            self.assertEqual([expected], exc.exception.args[0])

    def test_get_qualified_url_raise_exception_on_URLError(self):
        def mocked_urlopen(url):
            raise URLError('Hinky URL')

        with patch('deployer.utils.urlopen', mocked_urlopen):
            with self.assertRaises(DeploymentError) as exc:
                get_qualified_charm_url('cs:precise/mysql')
            expected = ('<urlopen error Hinky URL> '
                        '(https://api.jujucharms.com/charmstore/charm-info'
                        '?charms=cs:precise/mysql)')
            self.assertEqual([expected], exc.exception.args[0])
