#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
""" 	Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
		All rights reserved.
		
		Redistribution and use in source and binary forms, with or without
		modification, are permitted provided that the following conditions
		are met:
		1. Redistributions of source code must retain the above copyright
		   notice, this list of conditions and the following disclaimer.
		2. Redistributions in binary form must reproduce the above copyright
		   notice, this list of conditions and the following disclaimer in the
		   documentation and/or other materials provided with the distribution.
		3. The name of the author may not be used to endorse or promote products
		   derived from this software without specific prior written permission.
		
		THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
		IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
		OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
		IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
		INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
		NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
		DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
		THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
		THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		Unit test cases.
		
"""
from __future__ import unicode_literals
import unittest
import os
import io
import logging
import logging.config

from simpletal import simpleTAL, simpleTALES

if (os.path.exists("logging.ini")):
    logging.config.fileConfig("logging.ini")
else:
    logging.basicConfig()


def simpleFunction():
    return "Hello World"


def nestedFunction():
    return {'nest': simpleFunction}


class ExistsTests (unittest.TestCase):

    def setUp(self):
        self.context = simpleTALES.Context()
        self.context.addGlobal('top', 'Hello from the top')
        self.context.addGlobal('alt', 'Wobble the way')
        self.context.addGlobal(
            'theMap', {'top': 'Hello', 'onelevel': {'top': 'Bye'}})
        self.context.addGlobal(
            'funcMap', {'simple': simpleFunction, 'nested': nestedFunction})
        self.context.addGlobal('topFunc', simpleFunction)

    def _runTest_(self, txt, result, errMsg="Error"):
        template = simpleTAL.compileHTMLTemplate(txt)
        file = io.StringIO()
        template.expand(self.context, file)
        realResult = file.getvalue()
        self.assertEqual(realResult, result, "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" %
                         (errMsg, txt, realResult, result, template))

    def testOneVarDoesExist(self):
        self._runTest_('<html tal:condition="exists:top">Top</html>', '<html>Top</html>', 'Exists check on single variable failed.'
                       )

    def testOneVarDoesNotExist(self):
        self._runTest_('<html tal:condition="exists:nosuchvar">Top</html>', '', 'Exists check on single variable that does not exist failed.'
                       )

    def testTwoVarDoesExist(self):
        self._runTest_('<html tal:condition="exists:nosuchvar | exists:top">Top</html>', '<html>Top</html>', 'Exists check on two variables failed.'
                       )

    def testTwoVarDoesNotExist(self):
        self._runTest_('<html tal:condition="exists:nosuchvar | exists:nosuchvar2">Top</html>', '', 'Exists check on two variables that dont exist failed.'
                       )

    def testOneFuncExist(self):
        self._runTest_('<html tal:condition="exists:topFunc">Top</html>', '<html>Top</html>', 'Exists check on one function failed.'
                       )

    def testTwoFuncExist(self):
        self._runTest_('<html tal:condition="exists:nosuchvar | exists:topFunc">Top</html>', '<html>Top</html>', 'Exists check on two function failed.'
                       )

    def testNothingExists(self):
        self._runTest_('<html tal:condition=exists:nothing>Top</html>', '<html>Top</html>', 'Nothing should exist!'
                       )


if __name__ == '__main__':
    unittest.main()
