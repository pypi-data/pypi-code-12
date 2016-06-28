# -*- coding: utf-8 -*-

from nose.tools import raises

from obscheme.exceptions import InvariantError
from obscheme.fields.string import StringField
from obscheme.schema import Schema, invariant
from obscheme.schemameta import SchemaMeta


########################################################################
class AccountSchema(Schema):

    account_id = StringField()
    first_name = StringField()
    last_name = StringField()
    nick_name = StringField()

    #----------------------------------------------------------------------
    @invariant
    def full_name_or_nick_name(self, first_name, last_name, nick_name):
        if (self.first_name.is_defined(first_name) or self.last_name.is_defined(last_name)) \
                and self.nick_name.is_defined(nick_name):
            return u'Specify either full name or nick name'


########################################################################
class AccountObject(object):
    __metaclass__ = SchemaMeta
    __schema__ = AccountSchema()


#----------------------------------------------------------------------
def test_invariant_success_1():
    account = AccountObject()
    account.first_name = 'Foo'
    account.last_name = 'Bar'


#----------------------------------------------------------------------
def test_invariant_success_2():
    account = AccountObject()
    account.nick_name = 'fubar'


#----------------------------------------------------------------------
@raises(InvariantError)
def test_invariant_fail():
    account = AccountObject()
    account.first_name = 'Foo'
    account.last_name = 'Bar'
    account.nick_name = 'fubar'
