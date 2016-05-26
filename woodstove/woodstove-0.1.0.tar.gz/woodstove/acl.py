'''
ACL Interface
'''

from woodstove import exceptions
from woodstove import boolean
from woodstove import context


class Rule(boolean.Operand):
    '''
    Base ACL Rule class
    '''

    def __bool__(self):
        '''
        Interface definition for ACL rules.

        :raise NotImplementedError: Rule class should not be used directly.
        '''
        raise NotImplementedError


class Group(Rule):
    '''
    Group membership rule
    '''

    def __init__(self, group):
        '''
        Setup the rule by saving the group name to check.

        :param group: The group that will be matched against.
        '''
        self.group = group

    def __bool__(self):
        '''
        Verify user is a member of group.
        '''
        try:
            user = context.ctx_get()['request'].user
        except KeyError:
            raise exceptions.AuthException("Missing user object")

        return self.group in user.groups()


class ACL(object):
    '''
    Base ACL class

    :Example:

        ACL(Group('foo')).verify(user, requeest)
    '''

    def __init__(self, expr):
        '''
        Setup the ACL

        :param expr: ACL rule expression
        '''
        self.expr = expr

    def verify(self):
        '''
        Ensure the user/request match the rules defined in this ACL.

        :param user: User making the request
        :param request: request instance
        '''
        if not self.expr:
            raise exceptions.AuthException("ACL (%s) not matched" % self.expr)
