#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Uses 'inspect' to log in a file the detailed execution of the code.
Thanks to Françoise. 2015-06-18
"""

####

import sys
import inspect

OUTFILE = None
DEFAULT_OUTFILE = "/tmp/ktbs-inspector.log"

def inspectcode(frame, event, arg):
    """
    System’s trace function, which allows you to implement a Python source 
    code debugger in Python. 

    Trace functions should have three arguments: frame, event, and arg. 

    :param frame: the current stack frame. 
    :param event: a string: 'call', 'line', 'return', 'exception', 'c_call', 
                  'c_return', or 'c_exception'. 
    :param arg: depends on the event type.
    """
    with open(OUTFILE, "a+") as f:
        #f.write('event: {0}\n'.format(event))
        if event in ("call", "line"):
            frame_info = inspect.getframeinfo(frame)
            #f.write('frame:\n{0}\n\n'.format(frame_info))
            code = frame.f_code
            if code.co_filename
            if event == "call":
                f.write('{0}: |{1}| [{2}] {3} - {4}\n'.format(frame.f_lineno, event, code.co_filename, code.co_name, frame.f_locals.keys()))

            if event == "line":
                #f.write('{0}: |{1}| [{2}] {3}\n'.format(frame.f_lineno, event, code.co_filename, code.co_name))
                #f.write('{0}: [{1}] {2}\n'.format(frame.f_lineno, code.co_filename, code.co_name))
                f.write('{0}: \t{1}\n'.format(frame.f_lineno, code.co_name))

    return inspectcode


def start_plugin(config):
    global OUTFILE
    if "inspector" in config.sections():
        OUTFILE = config.get("inspector", "output", raw=False, vals={
            "output": DEFAULT_OUTFILE,
        })
    else:
        OUTFILE = DEFAULT_OUTFILE
    sys.settrace(inspectcode)

def stop_plugin():
    sys.settrace(None)
