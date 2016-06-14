# -*- coding: utf-8 -*-
"""This class defines a class decorator useful for creating methods that handles transactionality
in automatical manner"""

from tran import TransactionStack


class TransactionalMethod(object):
    """Class decorator for transactional methods"""
    def __init__(self, transactionName=''):
        """Function decorator for transactional methods.
        The transactionName is the name the transaction receives"""
        self._transactionName = transactionName

    def __call__(self, method):
        """"""
        def wrapped_call(*args, **kwargs):
            """Code for transamodeltional method"""
            # If we are inside an open transaction, we dont open
            # another again. Instead, do the associated operations
            # and return his 'something changes?' return value
            if TransactionStack.InTransaction():
                return method(*args, **kwargs)
            # Ok, we on top of new transaction. We do our work,
            # commit changes or rollback when no changes or exception happens
            import traceback
            import sys
            try:
                TransactionStack.DoBeginTransaction(self._transactionName)
                value = method(*args, **kwargs)
                if value:
                    TransactionStack.DoCommit()
                else:
                    TransactionStack.DoRollback()
                return value
            except Exception as inst:
                traceback.print_exc(file=sys.stdout)
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst
                TransactionStack.DoRollback()
                raise inst
        return wrapped_call
