# -*- coding: utf-8 -*-
"""
    koalaverify.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Generate verification tokens to be used for things such as password resets.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""

import koalacore
import logging
from oauthlib.common import generate_client_id, UNICODE_ASCII_CHARACTER_SET
import datetime
from google.appengine.ext import ndb
from google.appengine.ext.db import TransactionFailedError

__author__ = 'Matt Badger'


class VerificationToken(koalacore.Resource):
    token_uid = koalacore.ResourceProperty(title=u'Token UID')
    token = koalacore.ResourceProperty(title=u'Token')
    expires = koalacore.ResourceProperty(title=u'Token Expires')
    redirect_uri = koalacore.ResourceProperty(title=u'Token Redirect URI')

    def __init__(self, **kwargs):

        if 'token' not in kwargs or kwargs['token'] is None:
            token = generate_client_id(length=32, chars=UNICODE_ASCII_CHARACTER_SET)
            kwargs['token'] = token
            kwargs['uid'] = token

        expires_in = 720
        if 'expires_in' in kwargs:
            expires_in = int(kwargs['expires_in'])
            del kwargs['expires_in']

        if 'expires' not in kwargs or kwargs['expires'] is None:
            kwargs['expires'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in)

        super(VerificationToken, self).__init__(**kwargs)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        return datetime.datetime.utcnow() >= self.expires


class NDBVerificationTokenModel(ndb.Expando):
    """
    A VerificationToken which includes a token_uid (user_id) and a valid redirect route name

    Fields:
    * :attr:`token_uid` ref to a user/unique entity (implementation of user/entity is not relevant here)
    * :attr:`token` Verification token
    * :attr:`expires` Date and time of token expiration, in DateTime format
    * :attr:`redirect_uri` Redirect uri, if applicable
    """
    token_uid = ndb.StringProperty('vttuid', indexed=False)
    token = ndb.StringProperty('vtt', indexed=False)
    expires = ndb.DateTimeProperty('vte', indexed=False)
    redirect_uri = ndb.StringProperty('vtru', indexed=False)


class VerificationTokenNDBInterface(koalacore.NDBEventedInterface):
    _datastore_model = NDBVerificationTokenModel
    _resource_object = VerificationToken

    @classmethod
    def _convert_string_to_ndb_key(cls, datastore_key):
        # The id passed to this function if actually token, which is the ndb.Key.id
        # We therefore need to convert it to a proper ndb key before passing it on to the get function
        converted_key = cls.build_resource_uid(desired_id=datastore_key)
        return super(VerificationTokenNDBInterface, cls)._convert_string_to_ndb_key(datastore_key=converted_key)


class Verification(object):
    @classmethod
    def generate(cls, token_uid, redirect_uri=None, **kwargs):
        new_token = VerificationToken(token_uid=token_uid, redirect_uri=redirect_uri, **kwargs)
        VerificationTokenNDBInterface.insert(resource_object=new_token)

        return new_token.token

    @classmethod
    def verify(cls, token, token_uid=None, redirect_uri=None):
        # transactionally execute verify
        try:
            return ndb.transaction(lambda: cls._verify_token(token=token, token_uid=token_uid, redirect_uri=redirect_uri), retries=1)
        except TransactionFailedError:
            # This generally means that the token was valid but that the delete failed, implying that another thread
            # has already used the token. In theory this is a very rare occurrence.
            return False, u'Token has expired'


    @classmethod
    def _verify_token(cls, token, token_uid, redirect_uri):
        token_instance = VerificationTokenNDBInterface.get(resource_uid=token)

        if not token_instance:
            logging.error(u'Token {} is invalid'.format(token))
            return False, u'Token is invalid.'

        if token_instance.is_expired():
            logging.error(u'Token {} has expired'.format(token))
            return False, u'Token has expired.'

        if token_uid is not None:
            if token_instance.token_uid != token_uid:
                logging.error(u'Token {} UID mismatch'.format(token))
                return False, u'Token UID does not match stored value'

        if redirect_uri is not None:
            if token_instance.redirect_uri != redirect_uri:
                logging.error(u'Token {} Redirect URI mismatch'.format(token))
                return False, u'Redirect URI does not match stored value.'

        # If we get this far then the token is valid and we need to delete it - the token can only be valid once
        VerificationTokenNDBInterface.delete(resource_uid=token)
        return True, token_instance
