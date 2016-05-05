"""Tests for the views of the sprints app."""
from django.test import TestCase, RequestFactory  # NOQA

from mock import MagicMock

from .. import views


class BacklogViewTestCase(object):
    """Tests for the ``BacklogView`` view class."""
    longMessage = True

    def setUp(self):
        super(BacklogViewTestCase, self).setUp()
        self.mock_board = MagicMock()

        mock_list = MagicMock()
        mock_list.name = 'Foobar'
        self.mock_backlog = MagicMock()
        self.mock_backlog.name = 'Backlog'
        self.mock_lists = [mock_list, self.mock_backlog]
        mock_card1 = MagicMock()
        mock_card1.id = 1
        mock_card1.name = 'Foobar'
        mock_card2 = MagicMock()
        mock_card2.id = 2
        mock_card2.name = 'Something (5)'
        mock_card3 = MagicMock()
        mock_card3.id = 3
        mock_card3.name = 'Something else (120)'

        self.mock_backlog.list_cards.return_value = [
            mock_card1, mock_card2, mock_card3]
        views.TrelloClient.get_board = MagicMock(return_value=self.mock_board)
        self.mock_board.get_lists.return_value = self.mock_lists

    def test_view(self):
        req = RequestFactory().get('/')
        resp = views.BacklogView.as_view()(req)
        self.assertEqual(resp.status_code, 200, msg=('Should be callable'))

        req = RequestFactory().get('/?board=foo&rate=100')
        resp = views.BacklogView.as_view()(req)
        self.assertEqual(resp.status_code, 200, msg=('Should be callable'))
        self.assertEqual(resp.context_data['total_time'], 125, msg=(
            'Should iterate through all cards and add up the estimated time'))


class SprintViewTestCase(object):
    """Tests for the ``SprintView`` view class."""
    longMessage = True

    def setUp(self):
        super(SprintViewTestCase, self).setUp()
        self.mock_board = MagicMock()

        mock_list = MagicMock()
        mock_list.name = 'Foobar'
        self.mock_sprint = MagicMock()
        self.mock_sprint.name = 'Sprint-2014-10-20'
        self.mock_lists = [mock_list, self.mock_sprint]
        mock_card1 = MagicMock()
        mock_card1.id = 1
        mock_card1.short_id = 1
        mock_card1.name = 'Foobar'
        mock_card2 = MagicMock()
        mock_card2.id = 2
        mock_card2.name = 'Something (5)'
        mock_card2.short_id = 2
        mock_card3 = MagicMock()
        mock_card3.id = 3
        mock_card3.short_id = 3
        mock_card3.name = 'Something else (120)'

        self.mock_sprint.list_cards.return_value = [
            mock_card1, mock_card2, mock_card3]
        views.TrelloClient.get_board = MagicMock(return_value=self.mock_board)
        self.mock_board.get_lists.return_value = self.mock_lists

        mock_entry1 = MagicMock()
        entry2_dict = {'description': 'blabla c2 blabla', 'minutes': 10}

        def getitem(name):
            return entry2_dict[name]

        mock_entry2 = MagicMock(spec_set=dict)
        mock_entry2.__getitem__.side_effect = getitem
        mock_entry3 = MagicMock()
        self.mock_entries = [mock_entry1, mock_entry2, mock_entry3]
        views.Freckle.get_entries = MagicMock(return_value=self.mock_entries)

    def test_view(self):
        req = RequestFactory().get('/')
        resp = views.SprintView.as_view()(req)
        self.assertEqual(resp.status_code, 200, msg=('Should be callable'))

        req = RequestFactory().get(
            '/?board=foobar&sprint=Sprint-2014-10-20&project=foobar&rate=100')
        resp = views.SprintView.as_view()(req)
        self.assertEqual(resp.status_code, 200, msg=('Should be callable'))
        self.assertEqual(resp.context_data['total_actual_time'], 10, msg=(
            'Should iterate through all Freckle items and calculate actual'
            ' time'))
