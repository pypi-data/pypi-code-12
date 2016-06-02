'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2016-06-02

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
import copy
from Tkinter import Tk
from tkFileDialog import asksaveasfilename

import mistune
import easygui
try:
    import svgwrite
except ImportError:
    pass
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

class Shell():
    def __init__(self, parent=None):
        self.report_markdown = ''
        self.report_html = ''
        #---
        self.savedir = os.path.dirname(__file__)
        #---
        self.Code = None
        #----
        self.float_display_precison = 4
        
    def assign_code(self, CodeObiect):
        self.Code = CodeObiect
        
    def run_oryginal(self):
        exec self.Code.code_oryginal in globals(), locals()
        
    def delete_tmpfile(self):
        filedir = os.path.dirname(self.Code.script_path)
        for content in os.listdir(filedir):
            if 'tmp_seepy' in content :
                os.remove(filedir + '/' + content)

    def run_parsed(self):
        self.report_markdown = ''
        self.report_html = ''
        self._id = 1
        #-----------------------------------------------------------------
        # Here are functions needed in namespace where parsed code is run
        #-----------------------------------------------------------------
        def r_comment(object):
            self.report_markdown += str(object) + '\n\n'
        
        def r_adj(text = 'text', link = 'link', comment = 'somecomment'):
            href='[{0}]({1}) {2}'.format(text, link, comment)
            self.report_markdown += href +'\n\n'
            
        def r_img(imagename):
            image_path = os.path.dirname(self.Code.script_path) + '/' + imagename
            self.report_markdown += '![Alt text](%s)\n\n' % image_path

        def r_plt(pltObject):
            if pltObject.__package__ == 'matplotlib':
                name = 'tmp_seepy_' + str(self._id) + '.png'
                image_path = os.path.dirname(self.Code.script_path) + '/' + name
                pltObject.savefig(image_path, dpi=(60))
                self.report_markdown += '![Alt text](%s)\n\n' % image_path
                self._id += 1
            else :
                pass
                
        def r_tex(string):
            plt.figure(frameon=False)
            plt.axes(frameon=0)
            if string[0] != '$' and string[-1] != '$':
                string = '$' + string + '$'
            plt.text(0.0, 0.0, string, fontsize=600)
            plt.xticks(())
            plt.yticks(())
            plt.tight_layout()
            name = 'tmp_seepy_' + str(self._id) + '.png'
            image_path = os.path.dirname(self.Code.script_path) + '/' + name
            plt.savefig(image_path, bbox_inches='tight', dpi=(2))
            plt.close()
            self.report_markdown += '![Alt text](%s)\n\n' % image_path
            self._id += 1

        def r_codetex(string):
            r_tex(codeformat(string))
        
        def codeformat(string):
            string = string.replace('**', '^')
            string = string.replace('math.', '')
            return string
        
        def r_svg(svgObject):
            name = 'tmp_seepy_' + str(self._id) + '.svg'
            image_path = os.path.dirname(self.Code.script_path) + '/' + name
            if type(svgObject) is str:
                svg_file = open(image_path, "w")
                svg_file.write(svgObject)
                self.report_markdown += '![Alt text](%s)\n\n' % image_path
                svg_file.close()
                self._id += 1
            elif type(svgObject) is svgwrite.drawing.Drawing:
                svg_file = open(image_path, "w")
                svg_file.write(svgObject.tostring())
                self.report_markdown += '![Alt text](%s)\n\n' % image_path
                svg_file.close()
                self._id += 1
            else:
                pass

        def vars_formated(variables = vars()):
            out = copy.copy(variables)
            for key in out:
                if type(out[key]) is float:
                    out[key] = round(out[key], self.float_display_precison)
            return out
        #-----------------------------------------------------------------
        # Here the code_parsed is finally executed
        #-----------------------------------------------------------------
        exec self.Code.code_parsed in locals(), locals()
        #-----------------------------------------------------------------
        #---so the report_markdown has been creted-----------------------
        #---and mistune is used to get report_html from report_markdown
        self.report_html = mistune.markdown(self.report_markdown)
        #-----------------------------------------------------------------
        self._id = 0
        
    def show_report_markdown(self):
        easygui.codebox(title = 'report_markdown', text = self.report_markdown)
        
    def show_report_html(self):
        easygui.codebox(title = 'report_html', text = self.report_html)

    def save_report_markdown(self, savedir = os.path.dirname(__file__), initfilename = 'new.md'):
        root = Tk()
        root.withdraw()
        filename = asksaveasfilename(   parent=root,
                                        title='Save as Markdown document',
                                        filetypes=[('Markdown document', '*.md')],
                                        initialdir=savedir, initialfile=initfilename    )
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
    #---
    #ScriptCode.openFile()
    #Environment.run_parsed()
    #Environment.run_oryginal()
    #----
    #Environment.show_report_markdown()
    #Environment.show_report_html()