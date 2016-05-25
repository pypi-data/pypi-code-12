# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:50:30 2015

Copyright (C) 2016  Bloodywing

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License

@author: bloodywing
"""

import requests
from requests.utils import urlparse

version = 1.0  # Kwicks mapi version


class KwickError(Exception):

    def __init__(self, msg):
        self.msg = msg['errorMsg']

    def __str__(self):
        return repr(self.msg)


class Kwick(object):

    session = None
    mobile_session = None
    superapi_session = None
    cookie = None

    superapi_host = 'http://www.kwick.de'
    host = 'http://mapi.kwick.de/{version}'.format(version=version)
    mobile_host = 'http://m.kwick.de'
    response = None

    def __init__(self, session=None, mobile_session=None, superapi_session=None):
        if not session:
            self.session = requests.Session()
        if not mobile_session:
            self.mobile_session = requests.Session()
        if not superapi_session:
            self.superapi_session = requests.Session()

    def request(self, url, data=None, params=dict(), files=None, json=True, mobile=False, quirk=False, post=False):
        if data or post:
            method = 'POST'
        else:
            method = 'GET'

        if json and mobile:
            params['__env'] = 'json'
        if mobile and data:
            data['jsInfo'] = 'true'
            data['browserInfo'] = 'requests # Version'

        if mobile:
            response = self.mobile_session.request(
                method=method, url=self.mobile_host + url, data=data, params=params)
        elif quirk:
            response = self.superapi_session.request(
                method=method, url=self.superapi_host + url, data=data, params=params)
        else:
            response = self.session.request(
                method=method, url=self.host + url, data=data, params=params, files=files)
        if json:
            try:
                if 'errorMsg' in response.json():
                    raise KwickError(response.json())
                else:
                    return response.json()
            except ValueError:
                return response.content
        return response.content

    def kwick_login(self, kwick_username, kwick_password):
        """
        Wenn erfolgreich:
            {'loggedIn': True,
             'session_id': 'ein hash',
             'session_name': 'a2K3j8G1',
             'userid': XXXXXXX}
        Der name der Session ist immer gleich
        """
        url = '/login'
        data = dict(
            kwick_username=kwick_username,
            kwick_password=kwick_password
        )
        r = self.request(url, data, mobile=True, quirk=False)
        if r:
            self.superapi_session.cookies.set('a2K3j8G1', self.mobile_session.cookies['a2K3j8G1'], domain=urlparse(self.superapi_host).netloc)
        return self.request(url, data)

    def kwick_logout(self):
        """
        Von kwick ausloggen
        """
        url = '/logout'
        return self.request(url)

    # User-Service
    def kwick_index(self, page, community=False, json=True):
        """
        docs: http://developer.kwick.com/index.php/User/index
        """
        url = '/index'
        if community:
            url = '/index/community/'
        params = dict(
            page=page
        )
        return self.request(url, params=params, json=json, mobile=True)

    def kwick_setstatus(self, statustext=None):
        url = '/index/setStatus'

        data = dict(
            statusText=statustext,
        )
        return self.request(url, data=data)

    def kwick_socialobject_delete(self, type, id):
        """
        This is not in the docs
        """
        url = '/socialobject/{type}/{id}/delete'.format(
            type=type,
            id=id
        )
        return self.request(url, mobile=True)

    def kwick_infobox(self):
        url = '/infobox'
        return self.request(url)

    def kwick_user(self, username, page=0, json=True):
        url = '/{username}'.format(
            username=username
        )
        return self.request(url, json=json, mobile=True)

    # Feed Service
    def kwick_feed(self, feedid, delete=False):
        """
        docs: http://developer.kwick.com/index.php/Feed/feed
        docs: http://developer.kwick.com/index.php/Feed/feed/feedid/delete
        warning: doesn't work at all
        Kwick has replaced this with socialobjects
        """
        if delete:
            url = '/feed/{feedid}/delete'.format(feedid=feedid)
        else:
            url = '/feed/{feedid}'.format(feedid=feedid)
        return self.request(url)

    # Message Service
    def kwick_message(self, page=0, folder=None, sender=None, channel=0, delete=False, show=False):
        """
        folder: recv, sent, parked, spam
        default: recv
        """
        if delete:
            url = '/message/delete/{folder}/{sender}/{channel}'.format(
                folder=folder,
                sender=sender,
                channel=channel
            )
        elif show:
            url = '/message/show/{folder}/{page}/{sender}/{channel}'.format(
                folder=folder,
                page=page,
                sender=sender,
                channel=channel
            )
        else:
            url = '/message/{page}/'.format(page=page)
            if folder:
                url = '/message/{page}/{folder}'.format(
                    page=page, folder=folder)

        return self.request(url)

    def kwick_message_send(self, receiver, msgtext):
        url = '/message/send'
        data = dict(
            receiver=receiver,
            msgText=msgtext,
        )
        return self.request(url, data)

    def kwick_message_reply(self, receiver, channel, msgtext):
        url = '/message/sendReply'
        data = dict(
            receiver=receiver,
            channel=channel,
            msgText=msgtext,
        )
        return self.request(url, data)

    def kwick_email(self, folder=None, page=0, delete=False):
        url = '/email/{page}/{folder}'.format(
            folder=folder,
            page=page
        )
        return self.request(url)

    def kwick_email_delete(self, folder, mailid):
        url = '/email/delete/{folder}/{mailid}'.format(
            folder=folder,
            mailid=mailid
        )
        return self.request(url)

    def kwick_email_show(self, folder, mailid):
        url = '/email/show/{folder}/{mailid}'.format(
            folder=folder,
            mailid=mailid
        )
        return self.request(url)

    def kwick_email_send(self, receiver, subject, content,
                         folder=None, replymessage=None, forwardmessage=None, mobile=False):
        url = '/email/send'

        if mobile:
            import re
            response = self.request('/email/create/', mobile=True, json=False, quirk=True, params=dict()).decode('utf-8')
            token = re.search('_token_=(\w+)', response).group(1)

        data = dict(
            receiver=receiver,
            subject=subject,
            content=content,
            folder=folder,
            replyMsg=replymessage,
            forwardMsg=forwardmessage,
            old_answer_forward='',
        )

        if mobile:
            params=dict(
                _token_=token
            )
            del data['folder']
            del data['replyMsg']
            del data['forwardMsg']

        if mobile:
            return self.request(url, data=data, params=params, mobile=mobile, quirk=True, json=False)

        return self.request(url, data=data)

    def kwick_email_contactsel(self, group=None, page=0):
        url = '/email/write/contactsel/{group}/{page}'.format(
            group=group,
            page=page
        )

        return self.request(url)

    def kwick_friends(self, page=0, group=None, showoffline=0, quirk=False):
        url = '/friends'

        if quirk:
            url = '/api%s' % url

        params = dict(
            page=page,
            group=group,
            showOffline=showoffline
        )
        return self.request(url, params=params, quirk=quirk)

    def kwick_friendrequests(self, page=0):
        url = '/friends/requests/{page}'.format(
            page=page
        )
        return self.request(url)

    def kwick_friendrequest(self, username, action, reason=None):
        """
        :parameter action accept|reject|create|withdraw
        """
        url = '/{username}/friendrequest/{action}'.format(
            username=username,
            action=action
        )
        if action == 'create':
            data = dict(reason=reason)
            return self.request(url, data=data, mobile=True)
        return self.request(url)

    def kwick_comment_create(self, type, id, text):
        """
        :parameter type Microblog|Profile_Photos_Photo|Profile_Blog_Entry|Profile_Change_Registration
        :parameter id userid___objectid Use the kwick_index() function for examples
        """

        url = '/socialobject/{type}/{id}/comment/create'.format(
            type=type,
            id=id,
        )
        data = dict(
            text=text
        )
        return self.request(url, data=data)

    def kwick_comments(self, type, id, limit=100, offset=0):
        url = '/socialobject/{type}/{id}/comment/find/{limit}/{offset}'.format(
            type=type,
            id=id,
            limit=limit,
            offset=offset,
        )

        return self.request(url)

    def kwick_comment_delete(self, type, id, commentid):
        url = '/socialobject/{type}/{id}/comment/{commentid}/delete'.format(
            type=type,
            id=id,
            commentid=commentid
        )
        return self.request(url)

    def kwick_like(self, type, id, dolike=1):
        """
        :parameter dolike 1|0 Removes like if 0
        """
        url = '/socialobject/{type}/{id}/like/{dolike}'.format(
            type=type,
            id=id,
            dolike=dolike
        )
        return self.request(url)

    def kwick_search_members(self, online=None, age_from=1, age_to=99, distance=0,
                             single=None, haspic=None, gender=3, limit=100, offset=0):
        """
        :parameter gender 0|1|2
        :parameter limit Anything between 0 and 20
        Kwick Docs are wrong
        """
        url = '/search/members'
        params = locals()
        params.pop('self')
        params.pop('url')
        return self.request(url, params=params)

    def kwick_fan_add(self, username):
        """
        :parameter username Any username
        Some people have become a fan disabled
        """
        url = '/{username}/fan/add'.format(
            username=username
        )
        return self.request(url)

    def kwick_fan_remove(self, username):
        """
        :parameter username Any username
        """
        url = '/{username}/fan/remove'.format(
            username=username
        )
        return self.request(url)

    def kwick_photos(self, username, page=0):
        url = '/{username}/photos'.format(
            username=username
        )
        params =dict(page=page)
        return self.request(url, params=params)

    def kwick_photo_show(self, username, albumid, id, page=0):
        url = '/{username}/photos/show/{albumid}/{id}/{page}'.format(
            username=username,
            albumid=albumid,
            id=id,
            page=page
        )
        return self.request(url)

    def kwick_photo_comments(self, username, albumid, id, limit=100):
        url = '/{username}/photos/{albumid}/{id}/comments'.format(
            username=username,
            albumid=albumid,
            id=id
        )

        params = dict(
            limit=limit
        )

        return self.request(url, params=params)

    def kwick_photo_upload(self, albumid, photo, title=None, desc=None, returnShortUrl=None, username='me'):
        """
        Kwick docs says this needs a username, but you can use anything you want here
        """
        url = '/{username}/photos/upload'.format(
            username=username
        )

        data = dict(
            albumid=albumid,
            title=title,
            description=desc,
            returnShortUrl=returnShortUrl
        )

        files = dict(
            photo=photo
        )

        return self.request(url, data=data, files=files)
