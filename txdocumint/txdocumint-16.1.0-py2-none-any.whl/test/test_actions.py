from testtools import TestCase
from testtools.matchers import Equals

from txdocumint import actions


class RenderHTMLTests(TestCase):
    """
    Tests for `txdocumint.actions.render_html`.
    """
    def test_no_base_uri(self):
        """
        Construct a ``render-html`` action without a base URI.
        """
        action, _ = actions.render_html(u'http://example.com/input1')
        self.assertThat(
            action,
            Equals({u'action': u'render-html',
                    u'parameters': {
                        u'input': u'http://example.com/input1'}}))

    def test_base_uri(self):
        """
        Construct a ``render-html`` action with a base URI.
        """
        action, _ = actions.render_html(u'http://example.com/input1',
                                        u'http://example.com/')
        self.assertThat(
            action,
            Equals({u'action': u'render-html',
                    u'parameters': {
                        u'input': u'http://example.com/input1',
                        u'base-uri': u'http://example.com/'}}))

    def test_parser(self):
        """
        Parse the output of the ``render-html`` action.
        """
        _, parser = actions.render_html(u'http://example.com/input1')
        result = {u'links': {u'result': [u'http://example.com/output1']}}
        self.assertThat(
            parser(result),
            Equals(u'http://example.com/output1'))


class ConcatenateTests(TestCase):
    """
    Tests for `txdocumint.actions.concatenate`.
    """
    def test_action(self):
        """
        Construct a ``concatenate`` action..
        """
        action, _ = actions.concatenate([u'http://example.com/input1',
                                         u'http://example.com/input2'])
        self.assertThat(
            action,
            Equals({u'action': u'concatenate',
                    u'parameters': {
                        u'inputs': [u'http://example.com/input1',
                                    u'http://example.com/input2']}}))

    def test_parser(self):
        """
        Parse the output of the ``concatenate`` action.
        """
        _, parser = actions.concatenate([u'http://example.com/input1',
                                         u'http://example.com/input2'])
        result = {u'links': {u'result': [u'http://example.com/output1']}}
        self.assertThat(
            parser(result),
            Equals(u'http://example.com/output1'))


class ThumbnailsTests(TestCase):
    """
    Tests for `txdocumint.actions.thumbnails`.
    """
    def test_action(self):
        """
        Construct a ``thumbnails`` action..
        """
        action, _ = actions.thumbnails(u'http://example.com/input1', 100)
        self.assertThat(
            action,
            Equals({u'action': u'thumbnails',
                    u'parameters': {
                        u'input': u'http://example.com/input1',
                        u'dpi': 100}}))

    def test_parser(self):
        """
        Parse the output of the ``thumbnails`` action.
        """
        _, parser = actions.thumbnails(u'http://example.com/input1', 100)
        result = {u'links': {u'results': [u'http://example.com/output1',
                                          u'http://example.com/output2']}}
        self.assertThat(
            parser(result),
            Equals([u'http://example.com/output1',
                    u'http://example.com/output2']))


class SplitTests(TestCase):
    """
    Tests for `txdocumint.actions.split`.
    """
    def test_action(self):
        """
        Construct a ``split`` action..
        """
        action, _ = actions.split(u'http://example.com/input1',
                                  [[1, 2], [2, 3]])
        self.assertThat(
            action,
            Equals({u'action': u'split',
                    u'parameters': {
                        u'input': u'http://example.com/input1',
                        u'page-groups': [[1, 2], [2, 3]]}}))

    def test_parser(self):
        """
        Parse the output of the ``split`` action.
        """
        _, parser = actions.split(u'http://example.com/input1',
                                  [[1, 2], [2, 3]])
        result = {u'links': {u'results': [u'http://example.com/output1',
                                          u'http://example.com/output2']}}
        self.assertThat(
            parser(result),
            Equals([u'http://example.com/output1',
                    u'http://example.com/output2']))


class MetadataTests(TestCase):
    """
    Tests for `txdocumint.actions.metadata`.
    """
    def test_action(self):
        """
        Construct a ``metadata`` action..
        """
        action, _ = actions.metadata(u'http://example.com/input1')
        self.assertThat(
            action,
            Equals({u'action': u'metadata',
                    u'parameters': {
                        u'input': u'http://example.com/input1'}}))

    def test_parser(self):
        """
        Parse the output of the ``metadata`` action.
        """
        _, parser = actions.metadata(u'http://example.com/input1')
        result = {u'body': {u'page-count': 3,
                            u'title': u'Hello World'}}
        self.assertThat(
            parser(result),
            Equals({u'page-count': 3,
                    u'title': u'Hello World'}))


class SignTests(TestCase):
    """
    Tests for `txdocumint.actions.sign`.
    """
    def test_action(self):
        """
        Construct a ``sign`` action..
        """
        action, _ = actions.sign([u'http://example.com/input1',
                                  u'http://example.com/input2'],
                                 u'c', u'l', u'r')
        self.assertThat(
            action,
            Equals({u'action': u'sign',
                    u'parameters': {
                        u'inputs': [u'http://example.com/input1',
                                    u'http://example.com/input2'],
                        u'certificate-alias': u'c',
                        u'location': u'l',
                        u'reason': u'r'}}))

    def test_parser(self):
        """
        Parse the output of the ``sign`` action.
        """
        _, parser = actions.sign([u'http://example.com/input1',
                                  u'http://example.com/input2'],
                                 u'c', u'l', u'r')
        result = {u'links': {u'results': [u'http://example.com/output1',
                                          u'http://example.com/output2']}}
        self.assertThat(
            parser(result),
            Equals([u'http://example.com/output1',
                    u'http://example.com/output2']))


class CrushTests(TestCase):
    """
    Tests for `txdocumint.actions.crush`.
    """
    def test_action(self):
        """
        Construct a ``crush`` action..
        """
        action, _ = actions.crush(u'http://example.com/input1', u'text')
        self.assertThat(
            action,
            Equals({u'action': u'crush',
                    u'parameters': {
                        u'input': u'http://example.com/input1',
                        u'compression-profile': u'text'}}))

    def test_parser(self):
        """
        Parse the output of the ``crush`` action.
        """
        _, parser = actions.crush(u'http://example.com/input1', u'text')
        result = {u'links': {u'result': [u'http://example.com/output1']}}
        self.assertThat(
            parser(result),
            Equals(u'http://example.com/output1'))
