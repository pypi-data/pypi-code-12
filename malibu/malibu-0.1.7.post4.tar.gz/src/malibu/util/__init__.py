# -*- coding: utf-8 -*-
import glob
import inspect
import os

modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and not
           f.endswith('__init__.py') and os.path.isfile(f)]


def get_caller():
    """ Inspects the call stack to determine the path of a caller.
        Returns a string representing the full path to the caller.
    """

    # If we want to get the "caller" of a function, from this context we
    # must go backwards by two layers. The first frame is the current frame.
    # The second frame would be the function that calls get_caller().
    # The third frame is the frame we want to know the identity of.

    # The named tuple, Traceback, looks like this:
    #  Traceback(filename, lineno, function, code_context, index)

    frame = inspect.currentframe()
    # Get a list of frames up to two outside of the current frame1.
    callstack = inspect.getouterframes(frame, 2)
    # callstack is [Traceback(...), ...]
    # Grab the outermost frame
    caller = callstack[2][0]
    # Pull the Traceback tuple for the current frame.2
    callerinfo = inspect.getframeinfo(caller)

    # Determine if the function is a bound method.
    if 'self' in caller.f_locals:
        # Since the caller is a bound method, extract the 'self' reference
        # from the locals, then pull the class name from the instance class.
        caller_class = caller.f_locals['self'].__class__.__name__
    else:
        # There is no object this method is bound to -- it is a module
        # function.
        caller_class = None

    # Get the FQN of the module that the calling frame belongs to.
    caller_module = inspect.getmodule(caller).__name__
    # callerinfo is Traceback(...)
    caller_name = callerinfo[2]

    # Check the determined caller class.
    if caller_class:
        # If there is a caller class, prepend it to the caller name.
        caller_string = "%s.%s" % (caller_class, caller_name)
    else:
        # The caller string is just the caller name by itself.
        caller_string = "%s" % (caller_name)

    # Check the determined caller module.
    if caller_module:
        # Prepend the caller module to the caller string.
        caller_string = "%s." % (caller_module) + caller_string

    return caller_string


def get_calling_frame():

    frame = inspect.currentframe()
    callstack = inspect.getouterframes(frame, 2)
    caller = callstack[2][0]

    return caller


def get_current():

    frame = inspect.currentframe()
    callstack = inspect.getouterframes(frame, 1)
    frame = callstack[1][0]
    frameinfo = inspect.getframeinfo(frame)

    if 'self' in frame.f_locals:
        current_class = frame.f_locals['self'].__class__.__name__
    else:
        current_class = None

    current_module = inspect.getmodule(frame).__name__
    current_name = frameinfo[2]

    if current_class:
        current_string = "%s.%s" % (current_class, current_name)
    else:
        current_string = "%s" % (current_name)

    if current_module:
        current_string = "%s." % (current_module) + current_string

    return current_string


def get_current_frame():

    frame = inspect.currentframe()
    callstack = inspect.getouterframes(frame, 1)
    caller = callstack[1][0]

    return caller
