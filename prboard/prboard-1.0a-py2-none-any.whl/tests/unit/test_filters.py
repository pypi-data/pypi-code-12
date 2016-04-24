import copy
import unittest
import mock

from github import PullRequest, Repository

from prboard import filters


class BaseFilterTest(unittest.TestCase):
    def setUp(self):
        self.kwargs = {"filter_value": "A Value In Caps", "wildcard": True}


class TestBaseFilter(BaseFilterTest):

    def test___init__(self):
        for filter_value in (1, [1, 2]):
            wildcard = True
            bf = filters.BaseFilter(filter_value, wildcard)
            self.assertEqual(bf.filter_value, filter_value)
            self.assertEqual(bf.wildcard, wildcard)

        # With filter_value as string
        filter_value = "A Value In Caps"
        wildcard = False
        bf = filters.BaseFilter(filter_value, wildcard)
        self.assertEqual(bf.filter_value, filter_value.lower())
        self.assertEqual(bf.wildcard, wildcard)

    def test_filter_on_raises_not_implemented_error(self):
        """
        Call to filter_on should raise NotImplemented error
        """
        bf = filters.BaseFilter(**self.kwargs)
        # Python 2.6 support
        self.assertRaises(NotImplementedError, getattr, bf, "filter_on")

    @mock.PropertyMock(filters.BaseFilter.filter_on)
    def test___call__(self, mock_filter_on):
        """ Test callable """
        kwargs = copy.copy(self.kwargs)
        bf = filters.BaseFilter(**kwargs)
        obj = mock.MagicMock(name="Test")
        mock_filter_on.return_on = "value"
        output = bf(obj)
        self.assertTrue(output)
        self.assertEqual(obj, bf.obj)

        # Test with wildcard as False and filter_on is not equal to filter_value
        kwargs['wildcard'] = False
        bf = filters.BaseFilter(**kwargs)
        output = bf(obj)
        self.assertFalse(output)
        self.assertEqual(obj, bf.obj)

        # Test with wildcard as False and filter_on is equal to filter_value
        mock_filter_on.return_on = kwargs['filter_value'].lower()
        bf = filters.BaseFilter(**kwargs)
        output = bf(obj)
        self.assertFalse(output)
        self.assertEqual(obj, bf.obj)


class TestPRFilter(BaseFilterTest):
    """ Test PR filter """
    def test_filter_on(self):
        """ Test filter_on method """
        obj = mock.MagicMock()
        obj.pr = mock.MagicMock(title='A Value In Caps', number=1)
        pf = filters.PRFilter(**self.kwargs)
        pf.obj = obj
        self.assertEqual(pf.filter_on, obj.pr.title.lower())
        self.assertTrue(pf(obj))


class TestMileStoneFilter(BaseFilterTest):
    """ Test PR milestone filter """
    def test_filter_on(self):
        """ Test filter_on method """
        kwargs = copy.copy(self.kwargs)
        kwargs['filter_value'] = "R1.2.11"
        obj = mock.MagicMock()
        obj.pr = mock.MagicMock(title='A Value In Caps', number=1, milestone='R1.2.11')
        pf = filters.MileStoneFilter(**kwargs)
        pf.obj = obj
        self.assertEqual(pf.filter_on, obj.pr.milestone.lower())
        self.assertTrue(pf(obj))


class TestRepoFilter(BaseFilterTest):
    """ Test Repo filter """
    def test_filter_on(self):
        """ Test filter_on method """
        kwargs = copy.copy(self.kwargs)
        kwargs['filter_value'] = "A Repo"
        obj = mock.Mock(spec=Repository)
        type(obj).name = mock.PropertyMock(return_value='A Repo')
        rf = filters.RepoFilter(**kwargs)
        rf.obj = obj
        self.assertEqual(rf.filter_on, obj.name.lower())
        self.assertTrue(rf(obj))


class TestPRNumberFilter(BaseFilterTest):
    """ Test PR filter """
    def test_filter_on(self):
        """ Test filter_on method """
        kwargs = copy.copy(self.kwargs)
        kwargs['filter_value'] = 1
        obj = mock.MagicMock()
        obj.pr = mock.Mock(spec=PullRequest, title='Test PR', number=1)
        pf = filters.PRNumberFilter(**self.kwargs)
        pf.obj = obj
        self.assertEqual(pf.filter_on, obj.pr.number)

    def test___call__(self):
        kwargs = copy.copy(self.kwargs)
        obj = mock.MagicMock()
        obj.pr = mock.MagicMock(title='Test PR', number=1)
        for filter_value in (10, 1):
            # Check for filter_values 10 and 1. First should return False, second should return True
            kwargs['filter_value'] = filter_value
            pf = filters.PRNumberFilter(**kwargs)
            self.assertTrue(pf(obj) == (filter_value == 1))


class TestLabelFilter(BaseFilterTest):
    def test_filter_on(self):
        """ Test filter_on method """
        kwargs = copy.copy(self.kwargs)
        labels = ['enhancement', 'bug']
        kwargs['filter_value'] = labels
        obj = mock.MagicMock()
        obj.pr = mock.Mock(spec=PullRequest, title='Test PR', number=1)
        type(obj).labels = mock.PropertyMock(return_value=labels)
        pf = filters.LabelFilter(**kwargs)
        pf.obj = obj
        self.assertEqual(pf.filter_on, obj.labels)

    def test___call__with_filter_value_as_list_pass(self):
        """ Test call with filter_value as a list and pr having all the labels """
        kwargs = copy.copy(self.kwargs)
        labels = ['enhancement', 'bug']
        kwargs['filter_value'] = labels
        obj = mock.MagicMock()
        obj.pr = mock.Mock(spec=PullRequest, title='Test PR', number=1)
        type(obj).labels = mock.PropertyMock(return_value=labels)
        lf = filters.LabelFilter(**kwargs)
        self.assertTrue(lf(obj))

    def test___call__with_filter_value_as_list_fail(self):
        """ Test call with filter_value as a list and pr not having all the labels"""
        kwargs = copy.copy(self.kwargs)
        labels = ['enhancement']
        kwargs['filter_value'] = labels + ['bug']
        obj = mock.MagicMock()
        obj.pr = mock.Mock(spec=PullRequest, title='Test PR', number=1)
        type(obj).labels = mock.PropertyMock(return_value=labels)
        lf = filters.LabelFilter(**kwargs)
        self.assertFalse(lf(obj))

    def test___call__with_filter_value_as_str_pass(self):
        """ Test call with filter_value as a str and the label of pr matching the label """
        kwargs = copy.copy(self.kwargs)
        labels = ['enhancement', 'bug']
        kwargs['filter_value'] = 'bug'
        obj = mock.MagicMock()
        obj.pr = mock.Mock(spec=PullRequest, title='Test PR', number=1)
        type(obj).labels = mock.PropertyMock(return_value=labels)
        lf = filters.LabelFilter(**kwargs)
        self.assertTrue(lf(obj))

    def test___call__with_filter_value_as_str_fail(self):
        """ Test call with filter_value as a str and the label of pr not matching the label """
        kwargs = copy.copy(self.kwargs)
        labels = ['enhancement', 'bug']
        kwargs['filter_value'] = 'duplicate'
        obj = mock.MagicMock()
        obj.pr = mock.Mock(spec=PullRequest, title='Test PR', number=1)
        type(obj).labels = mock.PropertyMock(return_value=labels)
        lf = filters.LabelFilter(**kwargs)
        self.assertFalse(lf(obj))
