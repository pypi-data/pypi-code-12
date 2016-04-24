#!/usr/bin/env python3
# coding: utf-8

import functools
import requests
from . import auth as authlib
from . import default
from . import error
from . import utils


class BaseAPIHandler(object):
    '''Base API handler

    Example:
    >>> h = BaseAPIHandler(None, default.H_ROOT, default.UA)
    >>> h.get('statuses/public_timeline', {'count': 3})
    [{'created_at': '....',
      'favorited': '...',
      'id': '...',
      'in_reply_to_status_id': '',
      'in_reply_to_user_id': '',
      'keyword': '...',
      'link': '...',
      'replies': [...],
      'source': '...',
      'target': {...},
      'text': '....',
      'user': {'followers_count': '...',
               'id': '...',
               'name': '...',
               'profile_image_url': '...',
               'screen_name': '...',
               'url': 'http://h.hatena.ne.jp/...'}},
     {...},
     {...}]
    '''
    def __init__(self, auth, root, user_agent):
        self.auth = auth
        self.root = root
        self.user_agent = user_agent

    def get(self, api, params=None):
        url = '{0}/{1}'.format(self.root, api)
        headers = {'User-Agent': self.user_agent}
        res = requests.get(url, headers=headers, auth=self.auth, params=params)
        utils.check_response(res)
        return res.json()

    def post(self, api, params=None, data=None, files=None):
        url = '{0}/{1}'.format(self.root, api)
        headers = {'User-Agent': self.user_agent}
        res = requests.post(url, headers=headers, auth=self.auth,
                            params=params, data=data, files=files)
        utils.check_response(res)
        return res.json()


class Applications(object):
    '''Handler for specific OAuth APIs

    - my(): applications/my
    - start(): applications/start
    '''
    def __init__(self, auth, user_agent=default.UA, root=default.N_ROOT):
        '''``auth`` must be a ``None``, ``BasicAuth`` or ``OAuth`` object.
        '''
        if not isinstance(auth, authlib.OAuth):
            raise error.HaikerError('first argument must be a OAuth object')
        self._handler = BaseAPIHandler(auth, root, user_agent)

    def my(self):
        return self._handler.get('applications/my.json')

    def start(self):
        return self._handler.post('applications/start')


class BaseAPICategory(object):
    def __init__(self, handler=None):
        if handler is None:
            handler = BaseAPIHandler(None, default.H_ROOT, default.UA)
        self._handler = handler


class Statuses(BaseAPICategory):
    '''Methods under statuses/*

    - public_timeline(body_formats, count, page, since)
    - keyword_timeline([required] word, count, page, since, body_formats, sort)
    - user_timeline(url_name, body_formats, count, page, since, media, sort)
    - friends_timeline(url_name, count, page, since, body_formats)
    - album(word, body_formats, count, page, since, sort)
    - update([required] keyword, [required] status,
             in_reply_to_status_id, source, files, body_formats)
    - show([required] eid, body_formats)
    - destroy([required] eid, [required] author_url_name, body_formats)
    - friends(url_name, page)
    - followers(url_name, page)
    - keywords(url_name, page, without_related_keywords)
    '''
    def public_timeline(self, body_formats=None,
                        count=None, page=None, since=None):
        api = 'statuses/public_timeline.json'
        params = {
            'body_formats': utils.comma(body_formats),
            'count': count, 'page': page, 'since': since,
        }
        return self._handler.get(api, params)

    def keyword_timeline(self, word, count=None, page=None, since=None,
                         body_formats=None, sort=None):
        api = 'statuses/keyword_timeline.json'
        params = {
                'word': word,
                'count': count, 'page': page, 'since': since,
                'body_formats': utils.comma(body_formats), 'sort': sort,
        }
        return self._handler.get(api, params)

    def user_timeline(self, url_name=None, body_formats=None, count=None,
                      page=None, since=None, media=None, sort=None):
        if url_name is None:
            api = 'statuses/user_timeline.json'
        else:
            api = 'statuses/user_timeline/{0}.json'.format(url_name)
        params = {
            'body_formats': utils.comma(body_formats), 'count': count,
            'page': page, 'since': since, 'media': media, 'sort': sort,
        }
        return self._handler.get(api, params)

    def friends_timeline(self, url_name=None, count=None, page=None,
                         since=None, body_formats=None):
        if url_name is None:
            api = 'statuses/friends_timeline.json'
        else:
            api = 'statuses/friends_timeline/{0}.json'.format(url_name)
        params = {
            'count': count, 'page': page, 'since': since,
            'body_formats': utils.comma(body_formats),
        }
        return self._handler.get(api, params)

    def album(self, word=None, body_formats=None,
              count=None, page=None, since=None, sort=None):
        api = 'statuses/album.json'
        params = {
            'body_formats': utils.comma(body_formats), 'count': count,
            'page': page, 'since': since, 'sort': sort, 'word': word,
        }
        return self._handler.get(api, params)

    def update(self, keyword, status, in_reply_to_status_id=None,
               source=None, files=None, body_formats=None):
        api = 'statuses/update.json'
        data = {
            'keyword': keyword,
            'in_reply_to_status_id': in_reply_to_status_id,
            'status': status, 'source': source,
            'body_formats': utils.comma(body_formats),
        }
        if files is None:
            multiple_files = None
        else:
            multiple_files = [('file', f) for f in files]
        return self._handler.post(api, None, data, multiple_files)

    def show(self, eid, body_formats=None):
        api = 'statuses/show/{0}.json'.format(eid)
        params = {'body_formats': utils.comma(body_formats)}
        return self._handler.get(api, params)

    def destroy(self, eid, author_url_name, body_formats=None):
        api = 'statuses/destroy/{0}.json'.format(eid)
        params = {
            'author_url_name': author_url_name,
            'body_formats': utils.comma(body_formats),
        }
        return self._handler.post(api, params)

    def friends(self, url_name=None, page=None):
        if url_name is None:
            api = 'statuses/friends.json'
        else:
            api = 'statuses/friends/{0}.json'.format(url_name)
        params = {'page': page}
        return self._handler.get(api, params)

    def followers(self, url_name=None, page=None):
        if url_name is None:
            api = 'statuses/followers.json'
        else:
            api = 'statuses/followers/{0}.json'.format(url_name)
        params = {'page': page}
        return self._handler.get(api, params)

    def keywords(self, url_name=None, page=None,
                 without_related_keywords=None):
        if url_name is None:
            api = 'statuses/keywords.json'
        else:
            api = 'statuses/keywords/{0}.json'.format(url_name)
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'page': page,
            'without_related_keywords': is_excluded,
        }
        return self._handler.get(api, params)


class Favorites(BaseAPICategory):
    '''Methods under favorites/*

    - create([required] eid, body_formats):
    - destroy([required] eid, body_formats):
    '''
    def create(self, eid, body_formats=None):
        api = 'favorites/create/{0}.json'.format(eid)
        params = {'body_formats': utils.comma(body_formats)}
        return self._handler.post(api, params)

    def destroy(self, eid, body_formats=None):
        api = 'favorites/destroy/{0}.json'.format(eid)
        params = {'body_formats': utils.comma(body_formats)}
        return self._handler.post(api, params)


class Friendships(BaseAPICategory):
    '''Methods under friendships/*

    - show(url_name)
    - create(url_name)
    - destroy(url_name)
    '''
    def show(self, url_name):
        api = 'friendships/show/{0}.json'.format(url_name)
        return self._handler.get(api)

    def create(self, url_name):
        api = 'friendships/create/{0}.json'.format(url_name)
        return self._handler.post(api)

    def destroy(self, url_name):
        api = 'friendships/destroy/{0}.json'.format(url_name)
        return self._handler.post(api)


class KeywordsRelation(BaseAPICategory):
    '''Methods under keywords/relation/*

    - create([required] word1, [required] word2, without_related_keywords)
    - destroy([required] word1, [required] word2, without_related_keywords)
    '''
    def create(self, word1, word2, without_related_keywords=None):
        api = 'keywords/relation/create.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'word1': word1,
            'word2': word2,
            'without_related_keywords': is_excluded,
        }
        return self._handler.post(api, params)

    def destroy(self, word1, word2, without_related_keywords=None):
        api = 'keywords/relation/destroy.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'word1': word1,
            'word2': word2,
            'without_related_keywords': is_excluded,
        }
        return self._handler.post(api, params)


class Keywords(BaseAPICategory):
    '''Methods under keywords/*

    - show([required] word, without_related_keywords)
    - hot(without_related_keywords)
    - list(word, page, without_related_keyworde)
    - create([required] word, without_related_keywords)
    - destroy([required] word, without_related_keywords)
    - relation.create([required] word1, [required] word2, without_related_keywords)
    - relation.destroy([required] word1, [required] word2, without_related_keywords)
    '''
    def __init__(self, *args, **kwargs):
        self._relation = KeywordsRelation(*args, **kwargs)
        return super().__init__(*args, **kwargs)

    @property
    @functools.wraps(KeywordsRelation)
    def relation(self):
        return self._relation

    @relation.setter
    def relation(self, value):
        self._relation = value

    def show(self, word, without_related_keywords=None):
        api = 'keywords/show.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'without_related_keywords': is_excluded,
            'word': word
        }
        return self._handler.get(api, params)

    def hot(self, without_related_keywords=None):
        api = 'keywords/hot.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {'without_related_keywords': is_excluded}
        return self._handler.get(api, params)

    def list(self, word=None, page=None, without_related_keywords=None):
        api = 'keywords/list.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'page': page,
            'without_related_keywords': is_excluded,
            'word': word,
        }
        return self._handler.get(api, params)

    def create(self, word, without_related_keywords=None):
        api = 'keywords/create.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'without_related_keywords': is_excluded,
            'word': word,
        }
        return self._handler.post(api, params)

    def destroy(self, word, without_related_keywords=None):
        api = 'keywords/destroy.json'
        is_excluded = utils.integer(without_related_keywords)
        params = {
            'without_related_keywords': is_excluded,
            'word': word,
        }
        return self._handler.post(api, params)


class Haiku(object):
    '''Haiku API Handler

    Example:
    >>> api = Haiku(auth)
    >>> api.public_timeline(count=3)
    [{'created_at': '...',
      'favorited': '...',
      'id': '...',
      'in_reply_to_status_id': '',
      'in_reply_to_user_id': '',
      'keyword': '...',
      'link': '...',
      'replies': [...],
      'source': '...',
      'target': {...},
      'text': '....',
      'user': {'followers_count': '...',
               'id': '...',
               'name': '...',
               'profile_image_url': '...',
               'screen_name': '...',
               'url': 'http://h.hatena.ne.jp/...'}},
     {...},
     {...}]
    '''
    def __init__(self, auth=None, user_agent=default.UA, root=default.H_ROOT):
        '''``auth`` must be a ``None``, ``BasicAuth`` or ``OAuth`` object.
        '''
        h = self._handler = BaseAPIHandler(auth, root, user_agent)
        self._auth = auth
        self._statuses = Statuses(h)
        self._favorites = Favorites(h)
        self._friendships = Friendships(h)
        self._keywords = Keywords(h)

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, value):
        self._auth = value
        self._handler.auth = value

    @property
    @functools.wraps(Statuses)
    def statuses(self):
        return self._statuses

    @property
    @functools.wraps(Favorites)
    def favorites(self):
        return self._favorites

    @property
    @functools.wraps(Friendships)
    def friendships(self):
        return self._friendships

    @property
    @functools.wraps(Keywords)
    def keywords(self):
        return self._keywords
