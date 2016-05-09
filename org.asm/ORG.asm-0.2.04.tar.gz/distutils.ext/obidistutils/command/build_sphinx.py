'''
Created on 10 mars 2015

@author: coissac
'''

try:
    from sphinx.setup_command import BuildDoc as ori_build_sphinx  # @UnresolvedImport
        
    class build_sphinx(ori_build_sphinx):
        '''Build Sphinx documentation in html, epub and man formats 
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
except ImportError:
    pass  