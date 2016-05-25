import os
import unittest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
from nose.tools import raises
from kwick import Kwick, KwickError, __version__

user = os.environ['kwick_user'] or 'test'
password = os.environ['kwick_password'] or 'changeme'
msg = 'kwickmapi-python Version: {0}'.format(__version__)


class testKwick(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.kwick = Kwick()
        resp = cls.kwick.kwick_login(user, password)
        assert 'session_name' in resp

    @classmethod
    def teardown_class(cls):
        resp = cls.kwick.kwick_logout()
        assert 'textMsg' in resp

    @raises(KwickError)
    def test_raises_kwick_login_error(self):
        self.kwick.kwick_login(user, 'qwertz')

    def test_index(self):
        resp = self.kwick.kwick_index(page=0)
        self.assertTrue('socialstream' in resp)
        resp = self.kwick.kwick_index(page=0, community=True)
        self.assertTrue('community' in resp and resp['community'] is True)

    @patch.object(Kwick, 'request')
    def test_infobox(self, mock):
        resp = self.kwick.kwick_infobox()
        mock.assert_called_with('/infobox')

    @patch.object(Kwick, 'request')
    def test_kwick_feed(self, mock):
        self.kwick.kwick_feed(1337, delete=False)
        mock.assert_called_with('/feed/1337')

    @patch.object(Kwick, 'request')
    def test_kwick_feed_delete(self, mock):
        self.kwick.kwick_feed(1337, delete=True)
        mock.assert_called_with('/feed/1337/delete')

    @patch.object(Kwick, 'request')
    def test_user(self, mock):
        testuser = 'kwick'
        resp = self.kwick.kwick_user(username=testuser)
        mock.assert_called_with(
            '/{0}'.format(testuser), json=True, mobile=True)

    @raises(KwickError)
    def test_user_notavail(self):
        not_availuser = 'ar5oih435llsv83252jkffSdfs'
        self.kwick.kwick_user(username=not_availuser)

    @patch.object(Kwick, 'request')
    def test_friends(self, mock):
        resp = self.kwick.kwick_friends()
        mock.assert_called_with(
            '/friends', quirk=False, params={'page': 0, 'group': None, 'showOffline': 0})

    def test_search_members(self):
        resp = self.kwick.kwick_search_members(gender=0)
        assert 'users' in resp
        resp = self.kwick.kwick_search_members(gender=0, distance=100)
        assert 'users' in resp
        resp = self.kwick.kwick_search_members(gender=0,
                                               online=1,
                                               single=1,
                                               distance=100,
                                               haspic=1)
        self.assertTrue('users' in resp)

    @patch.object(Kwick, 'request')
    def test_status(self, mock):
        resp = self.kwick.kwick_setstatus(statustext=msg)
        mock.assert_called_with('/index/setStatus', data={'statusText': msg})

    @patch.object(Kwick, 'request')
    def test_fan(self, mock):
        resp = self.kwick.kwick_fan_add(username='kwick')
        mock.assert_called_with('/kwick/fan/add')

    @patch.object(Kwick, 'request')
    def test_defan(self, mock):
        resp = self.kwick.kwick_fan_remove(username='kwick')
        mock.assert_called_with('/kwick/fan/remove')

    @patch.object(Kwick, 'request')
    def test_like(self, mock):
        self.kwick.kwick_like('Microblog', '123456___123456', 1)
        mock.assert_called_with(
            '/socialobject/Microblog/123456___123456/like/1')

    @patch.object(Kwick, 'request')
    def test_friendrequest(self, mock):
        self.kwick.kwick_friendrequest('kwick', 'create', msg)
        mock.assert_called_with('/kwick/friendrequest/create', data={
            'reason': msg,
        }, mobile=True)

        self.kwick.kwick_friendrequest('kwick', 'withdraw', msg)
        mock.assert_called_with('/kwick/friendrequest/withdraw')

    @patch.object(Kwick, 'request')
    def test_friendrequests(self, mock):
        self.kwick.kwick_friendrequests(0)
        mock.assert_called_with('/friends/requests/0')

    @patch.object(Kwick, 'request')
    def test_delete_socialobject(self, mock):
        self.kwick.kwick_socialobject_delete('Microblog', '123456___123456')
        mock.assert_called_with(
            '/socialobject/Microblog/123456___123456/delete', mobile=True)

    @patch.object(Kwick, 'request')
    def test_message_send(self, mock):
        self.kwick.kwick_message_send(user, msg)
        mock.assert_called_with(
            '/message/send', {'receiver': user, 'msgText': msg})

    @patch.object(Kwick, 'request')
    def test_message_reply(self, mock):
        self.kwick.kwick_message_reply(user, 0, msg)
        mock.assert_called_with(
            '/message/sendReply', {'receiver': user, 'channel': 0, 'msgText': msg})

    @patch.object(Kwick, 'request')
    def test_message_list(self, mock):
        self.kwick.kwick_message(page=0, folder='recv')
        mock.assert_called_with('/message/0/recv')

    @patch.object(Kwick, 'request')
    def test_message_show(self, mock):
        self.kwick.kwick_message(
            show=True, page=0, folder='recv', sender=user, channel=0)
        mock.assert_called_with('/message/show/recv/0/{0}/0'.format(user))

    @patch.object(Kwick, 'request')
    def test_message_delete(self, mock):
        self.kwick.kwick_message(
            delete=True, sender=123456, channel=0, folder='recv')
        mock.assert_called_with('/message/delete/recv/{0}/0'.format(123456))

    @patch.object(Kwick, 'request')
    def test_comment_create(self, mock):
        self.kwick.kwick_comment_create('Microblog', '123456___123456', msg)
        mock.assert_called_with(
            '/socialobject/Microblog/123456___123456/comment/create', data={'text': msg})

    @patch.object(Kwick, 'request')
    def test_comments(self, mock):
        self.kwick.kwick_comments(
            'Microblog', '123456___123456', limit=100, offset=0)
        mock.assert_called_with(
            '/socialobject/Microblog/123456___123456/comment/find/100/0')

    @patch.object(Kwick, 'request')
    def test_comment_delete(self, mock):
        self.kwick.kwick_comment_delete(
            'Microblog', '123456___123456', '7778_7778')
        mock.assert_called_with(
            '/socialobject/Microblog/123456___123456/comment/7778_7778/delete')

    @patch.object(Kwick, 'request')
    def test_email(self, mock):
        self.kwick.kwick_email(folder='recv', page=0)
        mock.assert_called_with('/email/0/recv')

    @patch.object(Kwick, 'request')
    def test_email_delete(self, mock):
        self.kwick.kwick_email_delete(folder='recv', mailid=123456)
        mock.assert_called_with('/email/delete/recv/123456')

    @patch.object(Kwick, 'request')
    def test_email_show(self, mock):
        self.kwick.kwick_email_show(folder='recv', mailid=123456)
        mock.assert_called_with('/email/show/recv/123456')

    @patch.object(Kwick, 'request')
    def test_email_contactsel(self, mock):
        self.kwick.kwick_email_contactsel(group='buddies', page=0)
        mock.assert_called_with('/email/write/contactsel/buddies/0')

    @patch.object(Kwick, 'request')
    def test_email_send(self, mock):
        self.kwick.kwick_email_send(
            receiver=user, subject='test', content=msg, )
        mock.assert_called_with('/email/send', data={'replyMsg': None, 'forwardMsg': None, 'old_answer_forward': '', 'replyMsg': None,
                                                     'content': msg, 'receiver': user, 'folder': None, 'subject': 'test'})

    @patch.object(Kwick, 'request')
    def test_photos(self, mock):
        self.kwick.kwick_photos(user, page=0)
        mock.assert_called_with('/{username}/photos'.format(username=user), params={'page': 0})

    @patch.object(Kwick, 'request')
    def test_photo_show(self, mock):
        self.kwick.kwick_photo_show(user, 0, 1, page='0')
        mock.assert_called_with('/{username}/photos/show/{albumid}/{id}/{page}'.format(
            username=user,
            albumid=0,
            id=1,
            page='0'
        ))

    @patch.object(Kwick, 'request')
    def test_kwick_photo_comments(self, mock):
        self.kwick.kwick_photo_comments(user, 0, 1, limit=100)
        mock.assert_called_with('/{username}/photos/{albumid}/{id}/comments'.format(
            username=user,
            albumid=0,
            id=1
        ), params=(dict(limit=100)))

    @patch.object(Kwick, 'request')
    def test_kwick_photo_upload(self, mock):
        dummy = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'dummy.jpg' )
        with open(dummy, 'rb') as f:
            self.kwick.kwick_photo_upload('own', photo=f, title='dummy', desc='Testing the api', returnShortUrl='', username=user)
            mock.assert_called_with('/{username}/photos/upload'.format(username=user), data=dict(
                albumid='own',
                title='dummy',
                description='Testing the api',
                returnShortUrl=''
            ), files=dict(
                photo=f
            ))
