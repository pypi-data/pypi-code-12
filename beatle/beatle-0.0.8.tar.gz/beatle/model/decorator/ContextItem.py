# -*- coding: utf-8 -*-

import tran


class ContextDeclaration(object):
    """Class decorator for context dclaration"""
    def __init__(self):
        """"""
        super(ContextDeclaration, self).__init__()

    def __call__(self, method):
        """"""
        def wrapped_call(*args, **kwargs):
            """Code for context method"""
            this = args[0]
            pf = args[1]
            if this._declare:
                path = this.path
                for element in path:
                    element.WriteContextsPrefixDeclaration(pf)
                method(*args, **kwargs)
                for element in path:
                    element.WriteContextsSufixDeclaration(pf)
        return wrapped_call


class ContextImplementation(object):
    """Class decorator for context implementation"""
    def __init__(self):
        """Initialice context for implementation"""
        super(ContextImplementation, self).__init__()

    def __call__(self, method):
        """"""
        def wrapped_call(*args, **kwargs):
            """Code for context method"""
            this = args[0]
            pf = args[1]
            if this._implement:
                path = this.path
                for element in path:
                    element.WriteContextsPrefixImplementation(pf)
                method(*args, **kwargs)
                for element in path:
                    element.WriteContextsSufixImplementation(pf)
        return wrapped_call


class ContextItem(tran.TransactionObject):
    """Implements a context item used"""
    def __init__(self, **kwargs):
        """Initialize context item"""
        self._name = kwargs.get('name', '')
        self._define = kwargs.get('define', '')
        self._enable = kwargs.get('enable', False)
        self._prefix_declaration = kwargs.get('prefix_declaration', '')
        self._sufix_declaration = kwargs.get('sufix_declaration', '')
        self._prefix_implementation = kwargs.get('prefix_implementation', '')
        self._sufix_implementation = kwargs.get('sufix_implementation', '')
        self._note = kwargs.get('note', '')
        super(ContextItem, self).__init__()

    def SaveState(self):
        """Do save state"""
        super(ContextItem, self).SaveState()

    def Delete(self):
        """Do a transactional delete for any object"""
        super(ContextItem, self).Delete()
