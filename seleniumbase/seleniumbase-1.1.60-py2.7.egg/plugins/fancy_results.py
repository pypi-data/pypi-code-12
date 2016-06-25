"""
The Fancy Results plugin displays test results with a fancy GUI.
"""

import uuid
import logging
import os
from nose.plugins import Plugin


class FancyResults(Plugin):
    """
    The Fancy Results plugin.
    """
    name = 'fancy_results'  # Usage: --with-fancy_results

    def __init__(self):
        super(FancyResults, self).__init__()
        self.successes = []
        self.failures = []
        self.errors = []

    def configure(self, options, conf):
        return
        import ipdb; ipdb.set_trace()
        #pass
        #""" Get the options. """
        super(FancyResults, self).configure(options, conf)
        self.options = options

    def unconfigure(self):
        import ipdb; ipdb.set_trace()

    def afterTest(self, test):
        """ After each testcase, show fancy results. """
        import ipdb; ipdb.set_trace()
        print "fin_1"
        pass

    def addSuccess(self, test, capt):
        self.successes.append(test.id())

    def addError(self, test, err, capt=None):
        self.errors.append("ERROR: " + test.id())

    def addFailure(self, test, err, capt=None, tbinfo=None):
        self.failures.append("FAILED: " + test.id())

    def finalize(self, result):
        import ipdb; ipdb.set_trace()
        print "fin"
        pass
