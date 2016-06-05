#!/usr/bin/env python3

import datetime


def list_of(type):
    """Return to_list such that to_list([x0, x1, ...]) returns
    [type(x0), type(x1), ...].
    """
    def to_list(x):
        return [type(e) for e in x]
    return to_list


def none_or(type):
    """Return to_type such that to_type(x) returns
    None if x is None else type(x).
    """
    def to_type(x):
        return None if x is None else type(x)
    return to_type


def to_datetime(x):
    """Convert a valid global date and time string
    (e.g. '2010-01-02T03:04:05Z') to the datetime.datetime object.
    """
    x = x.replace('Z', '+00:00').replace('T', ' ')
    x = x[:-3] + x[-2:]  # '...+XX:YY' -> '...+XXYY'
    try:
        return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z')
    except ValueError:
        return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f%z')


def _repr(self, *attrs):
    name = self.__class__.__name__
    body = ', '.join('{attr}={value!r}'.format(attr=a, value=getattr(self, a))
                     for a in attrs)
    return '<{name} {body}>'.format(name=name, body=body)


class Status(object):
    """Entry object"""
    __slots__ = (
        'link', 'created_at', 'favorited', 'haiku_text', 'html', 'html_touch',
        'html_mobile', 'id', 'in_reply_to_status_id', 'in_reply_to_user_id',
        'keyword', 'replies', 'source', 'target', 'text', 'user',
    )

    def __init__(self, json):
        super().__init__()
        self.link = str(json['link'])
        self.created_at = to_datetime(json['created_at'])
        self.favorited = int(json['favorited'])
        self.haiku_text = none_or(str)(json.get('haiku_text'))
        self.html = none_or(str)(json.get('html'))
        self.html_touch = none_or(str)(json.get('html_touch'))
        self.html_mobile = none_or(str)(json.get('html_mobile'))
        self.id = str(json['id'])
        raw = json.get('in_reply_to_status_id')
        self.in_reply_to_status_id = none_or(str)(raw)
        raw = json.get('in_reply_to_user_id')
        self.in_reply_to_user_id = none_or(str)(raw)
        self.keyword = none_or(str)(json.get('keyword'))
        self.replies = none_or(list_of(Status))(json.get('replies'))
        self.source = str(json['source'])
        self.target = none_or(Target)(json.get('target'))
        self.text = none_or(str)(json.get('text'))
        self.user = User(json['user'])

    def __repr__(self):
        return _repr(self, 'link')


class User(object):
    """User object"""
    __slots__ = (
        'followers_count', 'name', 'id', 'profile_image_url', 'screen_name',
        'url',
    )

    def __init__(self, json):
        super().__init__()
        self.followers_count = int(json['followers_count'])
        self.name = str(json['name'])
        self.id = str(json['id'])
        self.profile_image_url = str(json['profile_image_url'])
        self.screen_name = str(json['screen_name'])
        self.url = str(json['url'])

    def __repr__(self):
        return _repr(self, 'id')


class Keyword(object):
    """Keyword object"""
    __slots__ = (
        'entry_count', 'followers_count', 'link', 'related_keywords', 'title',
        'word', 'url_name',
    )

    def __init__(self, json):
        super().__init__()
        self.entry_count = int(json['entry_count'])
        self.followers_count = int(json['followers_count'])
        self.link = str(json['link'])
        raw = json.get('related_keywords')
        self.related_keywords = none_or(list_of(str))(raw)
        self.title = str(json['title'])
        self.word = str(json['word'])
        self.url_name = none_or(str)(json.get('url_name'))

    def __repr__(self):
        return _repr(self, 'word')


class Target(object):
    """Target object"""
    __slots__ = ('title', 'word', 'url_name',)

    def __init__(self, json):
        super().__init__()
        self.title = str(json['title'])
        self.word = str(json['word'])
        self.url_name = none_or(str)(json.get('url_name'))

    def __repr__(self):
        return _repr(self, 'word')
