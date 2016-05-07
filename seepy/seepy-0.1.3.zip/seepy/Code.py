'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2

This file is part of SeePy.
SeePy is a structural engineering design Python package.
http://struthon.org/

SeePy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

SeePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.x changes:
- xxxxxx
'''

import os
import re

from Tkinter import Tk
from tkFileDialog import askopenfilename, asksaveasfilename

class Code ():
    
    def __init__(self):
        #---
        self.script_path = ''
        self.savedir = os.path.dirname(__file__)
        #---
        self.code_oryginal = ''
        self.code_parsed = ''

    def parse(self, path = ''):
        if not path :
            path = self.script_path
        if not path :
            self.newFile('x_newtemplate.py')
            path = self.script_path
        f = open(path, 'r')
        script = f.read()
        self.code_oryginal = script
        
        '''
        Here the code_oryginal is changed in to code_parsed with re.sub() replace
        -------------------------------------------------------------------------
        '''
        
        #--Variable with one line comment syntax
        script = re.sub(r'(\w+)(.+)#!(.+)', r"\1\2 \nr_comment('\1 = %(\1)s \3' % vars())", script)
        
        #--One line comment syntax
        script = re.sub(r'#!(.+)', r"r_comment('\1' % vars())", script)
        
        #--Multi line comment syntax 
        script = re.sub(r"#!(.{1})'''(.+?)'''", r"r_comment('''\2''' % vars())", script, flags=re.DOTALL)
        
        #--Multi line python code showing syntax
        script = re.sub(r"#%code(.+?)#%", r"\1r_comment('''```\1```''' )", script, flags=re.DOTALL)
        
        #--Image showing syntax
        script = re.sub(r'#%img (.+)', r"r_image('\1')", script)
        
        '''
        -------------------------------------------------------------------------
        '''
        self.code_parsed = script 
        
    def openFile(self):
        #----filename to open tkinter dialog
        root = Tk()
        root.withdraw()
        initName = 'script'
        filename = askopenfilename(parent=root,title='Open script', filetypes=[('Python script', '*.py')], initialdir=self.savedir)
        if not filename == '':
            self.savedir = os.path.dirname(filename)
            self.script_path = filename
            self.parse()
        root.destroy()
            
    def newFile(self, template_path, info='Save as', initfilename='your_script'):
        root = Tk()
        root.withdraw()
        filename = asksaveasfilename(parent=root,title=info, filetypes=[('Python script', '*.py')], initialdir=self.savedir, initialfile=initfilename)
        if not filename == '':
            new_template = open(template_path, 'r').read()
            self.savedir = os.path.dirname(filename)
            text_file = open(filename, "w")
            text_file.write(new_template)
            text_file.close()
            self.script_path = filename
            self.parse()
        root.destroy()
        
# Test if main
if __name__ == '__main__':
    ScriptCode = Code()
    #ScriptCode.parse()
    ScriptCode.openFile()
    print ScriptCode.code_oryginal
    print '#########################################'
    print ScriptCode.code_parsed
    print ScriptCode.savedir
    #ScriptCode.openFile()
    #ScriptCode.newFile()