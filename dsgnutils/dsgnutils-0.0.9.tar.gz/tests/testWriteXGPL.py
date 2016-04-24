'''
Copyright 2015 define().

This file is part of dsgnutils.

dsgnutils is free software: you can redistribute it and/or modify it under the
terms of the Lesser GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

dsgnutils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the Lesser GNU General Public License for more
details.

You should have received a copy of the Lesser GNU General Public License along
with dsgnutils.  If not, see <http://www.gnu.org/licenses/>.
'''

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises

from dsgnutils.utils import *
from dsgnutils.writeXGPL import *
from dsgnutils.xgplReadOnly import *

g__license=g__gpl

class Test_writeXGPL(object):
    pwd=BashIOE('pwd').out[0]
    testdir='/tmp/test_writeXGPL/'
    defined=[
        {
            'rem':'tests comment-required, multiline-possible file type',
            'name':'main.py',
            'text':'print(\"hello world!\")',
            'run':'python main.py',
            'type':None
        },
        {
            'rem':'tests comment-required, line-comment-only file type',
            'name':'makefile',
            'text':'test:\n\t@echo hello world!',
            'run':'make -s',
            'type':None
        },
        {
            'rem':'tests comment-not-required file type',
            'name':'README.txt',
            'text':'hello world!',
            'run':'tail -n 1 README.txt',
            'type':None
        },
        {
            'rem':'tests shebangeling',
            'name':'shebang.sh',
            'text':'#!/bin/bash\n\necho hello world!',
            'run':'source shebang.sh',
            'type':None
        },
    ]
    undefined=[]
    @classmethod
    def setup_class(cls):
        testdir=Test_writeXGPL.testdir
        defined=Test_writeXGPL.defined
        if not os.path.isdir(testdir):
            os.makedirs(testdir)
        os.chdir(testdir)
        cmd=StringIO()
        for x in defined:
            cmd.write("echo '%s' > %s;\n"%(x['text'],shlex.quote(x['name'])))
        cmd.write('git init; git add -A; git commit -m "init"')
        BashIOE(cmd.getvalue())
    @classmethod
    def teardown_class(cls):
        pwd=Test_writeXGPL.pwd
        testdir=Test_writeXGPL.testdir
        os.chdir(pwd)
        if os.path.isdir(testdir):
            shutil.rmtree(testdir)
    def setup(self):
        pass
    def teardown(self):
        pass
    def test_match(self):
        rslt=mapFileType('README.txt')
        assert_equal(XGPL_Text,type(rslt))
    def test_Ignore(self):
        rslt=mapFileType('LICENSE')
        assert_equal(XGPL_Ignore,type(rslt))
    def test_hasLicence(self):
        tstFile='/tmp/test_g__template_vs_g__regex.txt'
        br=BashIOE('touch %s'%(tstFile))
        txtTyp=mapFileType(tstFile)
        txtTyp.writeLicense(g__license,tstFile,'{0}','{1}')
        ret=txtTyp.hasLicense(g__license,tstFile)
        assert_equal(True,ret)
        os.remove(tstFile)

    def test_defined(self):
        defined=Test_writeXGPL.defined
        #-------make sure hello world files 'run'------------------------------
        for x in defined[0:4]:
            rslt=BashIOE(x['run']).out[0]
            assert_equal('hello world!',rslt)
        #-------test type indentification on hello world files-----------------
        assert_equal(XGPL_ML,type(mapFileType(defined[0]['name'])))
        assert_equal(XGPL_L,type(mapFileType(defined[1]['name'])))
        assert_equal(XGPL_Text,type(mapFileType(defined[2]['name'])))
        assert_equal(XGPL_ML,type(mapFileType(defined[3]['name'])))
        #-------sanity check defined files, and fill in their types------------
        for x in defined:
            ty=mapFileType(x['name'])
            isDefined=isinstance(ty,XGPL_FileType)
            assert(True==isDefined)
            x['type']=ty
        #-------verify that licenses are not detected-------------------------
        for x in defined:
            print(x['name'])
            hasLicense=x['type'].hasLicense(g__license,x['name'])
            assert(False==hasLicense)
        #-------write XGPL definition-----------------------------------------
        writeXGPL(g__license,'nose','test',force=True)
        BashIOE('git add -A; git commit -m "adding lgpl def";')
        #-------verify that licenses are detected-----------------------------
        for x in defined:
            hasLicense=x['type'].hasLicense(g__license,x['name'])
            assert(True==hasLicense)
        #-------verify hello world files still run----------------------------
        for x in defined[0:4]:
            rslt=BashIOE(x['run']).out[0]
            assert_equal('hello world!',rslt)

if '__main__'==__name__:
    pass



    
