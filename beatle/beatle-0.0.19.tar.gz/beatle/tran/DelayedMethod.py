# -*- coding: utf-8 -*-

"""
    Introducing delayed methods
    ===========================

    A delayed method is a smart method that detects in what environment is invoked
    and avoid duplicated and expensive calls.

    In transactional-free context, a delayed method behaves like normal a method:
    do his work and returns.

    Meanwhile, in the context of any open transaction or undo/redo operation, a
    delayed method enqueues the call, avoiding duplicates for the end of the
    transactional operation.

    That results in reduction of redundant calls done, for example while deleting
    a big set of elements at once.

    Creating a delayed method with a decorator is elegant and simple: nothing
    changes from the user point of view.

    The main target of delayed methods is obviously graphical updates, but surprisingly
    the origin of this idea was to minimice code regeneration.

"""


from tran import TransactionStack


def DelayedMethod(fifo=True):
    """Delayad with precedence"""
    def decoration(method):
        """Function decorator for delayed methods."""
        def wrapped_call(*args, **kwargs):
            """Code for delayed method"""
            # If we are not in transactional context, simply do the call
            if not (TransactionStack.InTransaction() or TransactionStack.InUndoRedo()):
                # do inmmediate call
                return method(*args, **kwargs)
            # Skip explicit filtered calls
            if method in TransactionStack.delayedCallsFiltered:
                return
            # Ok, check the method inside the transaction
            entry = TransactionStack.delayedCalls.get(method, [])
            if (args, kwargs) in entry:
                return
            if entry:
                if fifo:
                    TransactionStack.delayedCalls[method].append((args, kwargs))
                else:
                    TransactionStack.delayedCalls[method].insert(0, (args, kwargs))
            else:
                TransactionStack.delayedCalls[method] = [(args, kwargs)]
        wrapped_call.inner = method
        return wrapped_call
    return decoration
