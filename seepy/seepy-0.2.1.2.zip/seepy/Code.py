'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.4 date 2016-06-05

This file is part of SeePy.
SeePy is a python script visualisation tool.
http://seepy.org/

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
'''

import os
import re

from Tkinter import Tk
from tkFileDialog import askopenfilename, asksaveasfilename
from tkSimpleDialog import askstring

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
        #-------------------------------------------------------------------------
        #Here the code_oryginal is changed in to code_parsed with re.sub() replace
        #-------------------------------------------------------------------------
        script = re.sub(r'\r\n', r'\n', script) #new line \n (Linux) vs \r\n (windows) problem
        #--Variable with one line comment syntax
        script = re.sub(    r'(\w+)(.+)#!(.+)',
                            r"\1\2 \nr_comment('\1 = %(\1)s \3' % vars_formated())",
                            script  )
        #--One line comment syntax
        script = re.sub(    r'#!(.+)',
                            r"r_comment('\1' % vars_formated())",
                            script  )
        #--Multi line comment syntax 
        script = re.sub(    r"#!(.{1})'''(.+?)'''",
                            r"r_comment('''\2''' % vars_formated())", 
                            script, flags=re.DOTALL )
        #--One line python code showing syntax
        script = re.sub(    r"(.+)#%code",
                            r"\1\nr_comment('''```\1```''' )",
                            script  )
        #--Multi line python code showing syntax
        script = re.sub(    r"#%code(.+?)#%", 
                            r"\1r_comment('''```\1```''' )",
                            script, flags=re.DOTALL )
        #--Image showing syntax
        script = re.sub(    r'#%img (.+)',
                            r"r_img('\1')", 
                            script  )
        #--Matplotlib plt figure syntax
        script = re.sub(    r'(\w+)(.+)#%plt',
                            r"\1\2 \nr_plt(\1)",
                            script)
        #--One line LaTex syntax comment rendering
        script = re.sub(    r'#%tex(.+)',
                            r"r_tex(r'\1' % vars())", 
                            script  )
        #--One line code rendering as LaTex syntax with replace ** to ^
        script = re.sub(    r'(.+)#%tex',
                            r"\1\nr_codetex(r'\1' % vars_formated())",
                            script  )
        #--Rendering SVG syntax from python string
        script = re.sub(    r'(\w+)(.+)#%svg',
                            r"\1\2 \nr_svg(\1)",
                            script)
        #--Adjustable wariable with one line comment syntax
        script = re.sub(r'#<<', r"#<<_idx_", script)
        no = 1
        while re.search(r"#<<_idx_", script):
            script = script.replace(r'#<<_idx_', r"#<<_id%s_" % no, 1)
            no += 1
        script = re.sub(    r'(\w+)(.+)#<<_(.+)_(.+)', 
                            r"\1\2 \nr_adj('\1 = %(\1)s' % vars_formated(),'\3','\4' % vars_formated())",
                            script  )        
        #--saving
        self.code_parsed = script 
        
    def openFile(self):
        root = Tk()
        root.withdraw()
        initName = 'script'
        filename = askopenfilename( parent=root,title='Open script',
                                    filetypes=[('Python script', '*.py')],
                                    initialdir=self.savedir )
        if not filename == '':
            self.savedir = os.path.dirname(filename)
            self.script_path = filename
            self.parse()
        root.destroy()
            
    def newFile(self, template_path, info='Save as', initfilename='your_script'):
        root = Tk()
        root.withdraw()
        filename = asksaveasfilename( parent=root,title=info,
                                        filetypes=[('Python script', '*.py')],
                                        initialdir=self.savedir, 
                                        initialfile=initfilename    )
        if not filename == '':
            new_template = open(template_path, 'r').read()
            self.savedir = os.path.dirname(filename)
            text_file = open(filename, "w")
            text_file.write(new_template)
            text_file.close()
            self.script_path = filename
            self.parse()
        root.destroy()
        
    def editCode(self, lineID = 'id1'):
        script = self.code_oryginal
        #---
        script = re.sub(r'#<<', r"#<<_idx_", script)
        no = 1
        while re.search(r"#<<_idx_", script):
            script = script.replace(r'#<<_idx_', r"#<<_id%s_" % no, 1)
            no += 1
        #---
        expresion = re.search(r'(\w+) = (.+) #<<_%s_'%lineID, script)
        variable = expresion.group(1)
        value = expresion.group(2)
        #---
        root = Tk()
        mouse_x = root.winfo_pointerx() # mouse x position
        mouse_y = root.winfo_pointery() # mouse y position
        root.geometry('%dx%d+%d+%d' % (0, 0, mouse_x + 40, mouse_y - 130)) # where the dialog is show
        root.update()
        root.withdraw()
        value = askstring(  parent=root,
                            title='Set new value',
                            prompt=variable +'=',
                            initialvalue=value  ) 
        root.destroy()         
        #---
        script = re.sub(    r'(\w+) = (.+)#<<_%s_'%lineID,
                            r'\1 = %s #<<_%s_'%(value, lineID),
                            script  )
        #---
        script = re.sub(r"#<<_id(.+)_", r'#<<', script)
        #---
        self.code_oryginal = script
        #---
        file = open(self.script_path, "r+")
        file.write(script)
        file.close()

# Test if main
if __name__ == '__main__':
    ScriptCode = Code()
    #ScriptCode.openFile()
    #ScriptCode.parse()
    #print ScriptCode.code_oryginal
    #print ScriptCode.code_parsed
    #print ScriptCode.savedir
    #ScriptCode.openFile()
    #ScriptCode.newFile()
    #ScriptCode.editCode()