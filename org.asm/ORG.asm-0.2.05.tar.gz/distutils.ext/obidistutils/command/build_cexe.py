'''
Created on 20 oct. 2012

@author: coissac
'''

from .build_ctools import build_ctools
from .build_exe import build_exe
from distutils.errors import DistutilsSetupError
from distutils import log
import os

class build_cexe(build_ctools):

    description = "build C/C++ executable distributed with Python extensions"


    def initialize_options(self):
        build_ctools.initialize_options(self)
        self.built_files = None


    def finalize_options(self):
        # This might be confusing: both build-cexe and build-temp default
        # to build-temp as defined by the "build" command.  This is because
        # I think that C libraries are really just temporary build
        # by-products, at least from the point of view of building Python
        # extensions -- but I want to keep my options open.

        build_cexe_dir = self.build_cexe
        build_ctools.finalize_options(self)

        if build_cexe_dir is None:
            self.build_cexe=None
            
        self.set_undefined_options('build',
                                   ('build_scripts',  'build_cexe'))

        self.set_undefined_options('build_files',
                                   ('files',  'built_files'))
                   
        self.executables   = self.distribution.executables
#         self.build_cexe = os.path.join(os.path.dirname(self.build_cexe),'cbinaries') 
#         self.mkpath(self.build_cexe)

        if self.executables:
            self.check_executable_list(self.executables)
                            

        # XXX same as for build_ext -- what about 'self.define' and
        # 'self.undef' ?

    def substitute_sources(self,exe_name,sources):
        """
        Substitutes source file name starting by an @ by the actual
        name of the built file (see --> build_files)
        """
        sources = list(sources)
        for i in range(len(sources)):
            message = "%s :-> %s" % (exe_name,sources[i])
            if sources[i][0]=='@':
                try:
                    filename = self.built_files[sources[i][1:]]
                except KeyError:
                    raise DistutilsSetupError(
                         'The %s filename declared in the source '
                         'files of the program %s have not been '
                         'built by the installation process' % (sources[i],
                                                                exe_name))
                sources[i]=filename
                log.info("%s changed to %s",message,filename)
            else:
                log.info("%s ok",message)

        return sources
 
    def run(self):

        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        build_exe.run(self)
        

   
