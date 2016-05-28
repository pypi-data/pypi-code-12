'''
Created on 10 mars 2015

@author: coissac
'''

from distutils import log
from obidistutils.serenity.checkpackage import install_requirements
from obidistutils.serenity.rerun import rerun_with_anothe_python
from obidistutils.serenity import is_serenity
import os
import sys

try:
    from sphinx.setup_command import BuildDoc as ori_build_sphinx
except ImportError:
    if not is_serenity() and install_requirements():
        log.info("Restarting installation with all dependencies ok")
        rerun_with_anothe_python(os.path.realpath(sys.executable))
    
class build_sphinx(ori_build_sphinx):
    '''
    Build Sphinx documentation in html, epub and man formats 
    '''

    description = __doc__

    def run(self):
        self.builder='html'
        self.finalize_options()
        ori_build_sphinx.run(self)
        self.builder='epub'
        self.finalize_options()
        ori_build_sphinx.run(self)
        self.builder='man'
        self.finalize_options()
        ori_build_sphinx.run(self)
    