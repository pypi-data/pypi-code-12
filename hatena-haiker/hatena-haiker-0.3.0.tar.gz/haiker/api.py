#!/usr/bin/env python3

import functools
import re
import requests
from . import error, types, utils


class BaseAPIHandler(object):
    """Base API handler

    Example:

    >>> h = haiker.api.BaseAPIHandler(
    ...         haiker.OAuth(
    ...             'MyConsumerKey', 'MyConsumerSecret',
    ...             'MyAccessToken', 'MyAccessTokenSecret'
    ...         ),
    ...         'http://h.hatena.ne.jp/api',
    ...         haiker.utils.DEFAULT_USER_AGENT
    ... )
    >>> statuses = h.get('/statuses/public_timeline.json', {'count': 3})
    >>> len(statuses)
    3
    >>> statuses[0]['created_at']
    '2010-01-02T03:04:05Z'
    >>> statuses[0]['user']['url']
    'http://h.hatena.ne.jp/xxxxxx/'
    """
    def __init__(self, auth, root, user_agent):
        super().__init__()
        self.auth = auth
        self.root = root
        self.user_agent = user_agent

    def _request(self, method, path, params=None, data=None, files=None):
        if re.search('[^a-zA-Z0-9./\\-_]|\\.\\.|//', path) is not None:
            raise ValueError('suspicious path: {0!r}'.format(path))
        url = self.root.rstrip('/') + '/' + path.lstrip('/')
        headers = {'User-Agent': self.user_agent}
        res = method(url, headers=headers, auth=self.auth,
                     params=utils.build_params(params),
                     data=utils.build_params(data),
                     files=files)
        res.raise_for_status()
        return res.json()

    def get(self, path, params=None):
        return self._request(requests.get, path, params=params)

    def post(self, path, params=None, data=None, files=None):
        return self._request(requests.post, path,
                             params=params, data=data, files=files)


class Haiker(object):
    """Handler for the Hatena Haiku RESTful API

    Example:

    >>> import haiker
    >>> auth = haiker.OAuth(
    ...     'MyConsumerKey', 'MyConsumerSecret',
    ...     'MyAccessToken', 'MyAccessTokenSecret'
    ... )
    >>> api = haiker.Haiker(auth)
    >>> statuses = api.public_timeline(count=3)
    >>> len(statuses)
    3
    >>> status = statuses[0]
    >>> status.created_at
    datetime.datetime(2010, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)
    >>> status.user.url
    'http://h.hatena.ne.jp/xxxxxx/'
    """
    @error.HaikerError.replace
    def __init__(self, auth=None, *,
                 user_agent=utils.DEFAULT_USER_AGENT,
                 root='http://h.hatena.ne.jp/api'):
        """auth is required to be None, a haiker.BasicAuth object
        or haiker.OAuth object.
        """
        super().__init__()
        self._handler = BaseAPIHandler(auth, root, user_agent)

    @property
    @error.HaikerError.replace
    def auth(self):
        return self._handler.auth

    @auth.setter
    @error.HaikerError.replace
    def auth(self, value):
        self._handler.auth = value

    # Timeline APIs
    @error.HaikerError.replace
    def public_timeline(self, *, body_formats=None, count=None, page=None,
                        since=None):
        """statuses/public_timeline"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/statuses/public_timeline.json'
        res = self._handler.get(path, params)
        return types.list_of(types.Status)(res)

    @error.HaikerError.replace
    def keyword_timeline(self, word, *, count=None, page=None, since=None,
                         body_formats=None, sort=None):
        """statuses/keyword_timeline"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/statuses/keyword_timeline.json'
        res = self._handler.get(path, params)
        return types.list_of(types.Status)(res)

    @error.HaikerError.replace
    def user_timeline(self, url_name=None, *, body_formats=None, count=None,
                      page=None, since=None, media=None, sort=None):
        """statuses/user_timeline"""
        params = utils.removed_dict(locals(), {'self', 'url_name'})
        if url_name is None:
            path = '/statuses/user_timeline.json'
        else:
            path = '/statuses/user_timeline/{0}.json'.format(url_name)
        res = self._handler.get(path, params)
        return types.list_of(types.Status)(res)

    @error.HaikerError.replace
    def friends_timeline(self, url_name=None, *, count=None, page=None,
                         since=None, body_formats=None):
        """statuses/friends_timeline"""
        params = utils.removed_dict(locals(), {'self', 'url_name'})
        if url_name is None:
            path = '/statuses/friends_timeline.json'
        else:
            path = '/statuses/friends_timeline/{0}.json'.format(url_name)
        res = self._handler.get(path, params)
        return types.list_of(types.Status)(res)

    @error.HaikerError.replace
    def album(self, *, body_formats=None, count=None, page=None,
              since=None, sort=None, word=None):
        """statuses/album"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/statuses/album.json'
        res = self._handler.get(path, params)
        return types.list_of(types.Status)(res)

    # Entry and star APIs
    @error.HaikerError.replace
    def update_status(self, keyword, status, *, in_reply_to_status_id=None,
                      source=None, files=None, body_formats=None):
        """statuses/update"""
        params = utils.removed_dict(locals(), {'self', 'files'})
        if files is not None:
            files = [('file', f) for f in files]
        path = '/statuses/update.json'
        res = self._handler.post(path, None, params, files)
        return types.Status(res)

    @error.HaikerError.replace
    def show_status(self, eid, *, body_formats=None):
        """statuses/show"""
        params = utils.removed_dict(locals(), {'self', 'eid'})
        path = '/statuses/show/{0}.json'.format(eid)
        res = self._handler.get(path, params)
        return types.Status(res)

    @error.HaikerError.replace
    def delete_status(self, eid, author_url_name, *, body_formats=None):
        """statuses/destroy"""
        params = utils.removed_dict(locals(), {'self', 'eid'})
        path = '/statuses/destroy/{0}.json'.format(eid)
        res = self._handler.post(path, params)
        return types.Status(res)

    @error.HaikerError.replace
    def add_star(self, eid, *, body_formats=None):
        """favorites/create"""
        params = utils.removed_dict(locals(), {'self', 'eid'})
        path = '/favorites/create/{0}.json'.format(eid)
        res = self._handler.post(path, params)
        return types.Status(res)

    @error.HaikerError.replace
    def remove_star(self, eid, *, body_formats=None):
        """favorites/destroy"""
        params = utils.removed_dict(locals(), {'self', 'eid'})
        path = '/favorites/destroy/{0}.json'.format(eid)
        res = self._handler.post(path, params)
        return types.Status(res)

    # User and keyword APIs
    @error.HaikerError.replace
    def show_user(self, url_name=None):
        """friendships/show"""
        if url_name is None:
            path = '/friendships/show.json'.format(url_name)
        else:
            path = '/friendships/show/{0}.json'.format(url_name)
        res = self._handler.get(path)
        return types.User(res)

    @error.HaikerError.replace
    def show_keyword(self, word, *, without_related_keywords=None):
        """keywords/show"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/show.json'
        res = self._handler.get(path, params)
        return types.Keyword(res)

    @error.HaikerError.replace
    def hot_keywords(self, *, without_related_keywords=None):
        """keywords/hot"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/hot.json'
        res = self._handler.get(path, params)
        return types.list_of(types.Keyword)(res)

    @error.HaikerError.replace
    def keyword_list(self, *, page=None, without_related_keywords=None,
                     word=None):
        """keywords/list"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/list.json'
        res = self._handler.get(path, params)
        return types.list_of(types.Keyword)(res)

    @error.HaikerError.replace
    def associate_keywords(self, word1, word2, *,
                           without_related_keywords=None):
        """keywords/relation/create"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/relation/create.json'
        res = self._handler.post(path, params)
        return types.Keyword(res)

    @error.HaikerError.replace
    def dissociate_keywords(self, word1, word2, *,
                            without_related_keywords=None):
        """keywords/relation/destroy"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/relation/destroy.json'
        res = self._handler.post(path, params)
        return types.Keyword(res)

    # Favorite APIs
    @error.HaikerError.replace
    def friends(self, url_name=None, *, page=None):
        """statuses/friends"""
        params = utils.removed_dict(locals(), {'self', 'url_name'})
        if url_name is None:
            path = '/statuses/friends.json'
        else:
            path = '/statuses/friends/{0}.json'.format(url_name)
        res = self._handler.get(path, params)
        return types.list_of(types.User)

    @error.HaikerError.replace
    def followers(self, url_name=None, *, page=None):
        """statuses/followers"""
        params = utils.removed_dict(locals(), {'self', 'url_name'})
        if url_name is None:
            path = '/statuses/followers.json'
        else:
            path = '/statuses/followers/{0}.json'.format(url_name)
        res = self._handler.get(path, params)
        return types.list_of(types.User)

    @error.HaikerError.replace
    def add_friend(self, url_name):
        """friendships/create"""
        path = '/friendships/create/{0}.json'.format(url_name)
        res = self._handler.post(path)
        return types.User(res)

    @error.HaikerError.replace
    def remove_friend(self, url_name):
        """friendships/destroy"""
        path = '/friendships/destroy/{0}.json'.format(url_name)
        res = self._handler.post(path)
        return types.User(res)

    @error.HaikerError.replace
    def favorite_keywords(self, url_name=None, *, page=None,
                          without_related_keywords=None):
        """statuses/keywords"""
        params = utils.removed_dict(locals(), {'self', 'url_name'})
        if url_name is None:
            path = '/statuses/keywords.json'
        else:
            path = '/statuses/keywords/{0}.json'.format(url_name)
        res = self._handler.get(path, params)
        return types.list_of(types.Keyword)

    @error.HaikerError.replace
    def add_favorite_keyword(self, word, *, without_related_keywords=None):
        """keywords/create"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/create.json'
        res = self._handler.post(path, params)
        return types.Keyword(res)

    @error.HaikerError.replace
    def remove_favorite_keyword(self, word, *, without_related_keywords=None):
        """keywords/destroy"""
        params = utils.removed_dict(locals(), {'self'})
        path = '/keywords/destroy.json'
        res = self._handler.post(path, params)
        return types.Keyword(res)
