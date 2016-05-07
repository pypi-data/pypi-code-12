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

import mistune
import easygui

from Tkinter import Tk
from tkFileDialog import asksaveasfilename

class Shell():
    def __init__(self, parent=None):
        self.report_markdown = ''
        self.report_html = ''
        #---
        self.savedir = os.path.dirname(__file__)
        #---
        self.Code = None
        
    def assign_code(self, CodeObiect):
        self.Code = CodeObiect
        
    def run_oryginal(self):
        exec self.Code.code_oryginal in globals(), locals()

    def run_parsed(self):
        self.report_markdown = ''
        self.report_html = ''
        #----------extra shell function--------------
        def r_comment(object):
            self.report_markdown += str(object) + '\n\n'
        def r_image(imagename):
            image_path = os.path.dirname(self.Code.script_path) + '/' + imagename
            print image_path
            self.report_markdown += '![Alt text](%s)\n\n' % image_path
        #----here is the code_parsed executing--------
        #---------------------------------------------
        exec self.Code.code_parsed in globals(), locals()
        #---------------------------------------------
        #---------------------------------------------
        self.report_html = mistune.markdown(self.report_markdown)
        #print vars()
        
    def show_report_markdown(self):
        easygui.codebox(title = 'report_markdown', text = self.report_markdown)
        
    def show_report_html(self):
        easygui.codebox(title = 'report_html', text = self.report_html)

    def save_report_markdown(self, savedir = os.path.dirname(__file__), initfilename = 'new.md'):
        root = Tk()
        root.withdraw()
        filename = asksaveasfilename(parent=root,title='Save as Markdown document', filetypes=[('Markdown document', '*.md')], initialdir=savedir, initialfile=initfilename)
        if not filename == '':
            self.savedir = os.path.dirname(filename)
            md_file = open(filename, "w")
            md_file.write(self.report_markdown)
            md_file.close()
        root.destroy()

# Test if main
if __name__ == '__main__':
    Environment = Shell()
    from Code import Code
    ScriptCode = Code()
    Environment.assign_code(ScriptCode)
    #---reloading--
    ScriptCode.openFile()
    Environment.run_parsed()
    #Environment.run_oryginal()
    #----
    Environment.show_report_markdown()
    #Environment.show_report_html()