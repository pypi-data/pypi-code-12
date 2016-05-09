'''
Created on 13 fevr. 2014

@author: coissac
'''

from distutils import log
import os


from distutils.errors import DistutilsSetupError

try:
    from Cython.Distutils import build_ext  as ori_build_ext  # @UnresolvedImport
    from Cython.Compiler import Options as cython_options  # @UnresolvedImport
    class build_ext(ori_build_ext):
    
        
        def modifyDocScripts(self):
            build_dir_file=open("doc/sphinx/build_dir.txt","w")
            print(self.build_lib,file=build_dir_file)
            build_dir_file.close()
            
        def initialize_options(self):
            ori_build_ext.initialize_options(self)  # @UndefinedVariable
            self.littlebigman = None
            self.built_files = None
    
        
        def finalize_options(self):
            ori_build_ext.finalize_options(self)  # @UndefinedVariable
    
            self.set_undefined_options('littlebigman',
                                       ('littlebigman',  'littlebigman'))
            
            self.set_undefined_options('build_files',
                                       ('files',  'built_files'))
    
            self.cython_c_in_temp = 1
                       
            if self.littlebigman =='-DLITTLE_END':
                if self.define is None:
                    self.define=[('LITTLE_END',None)]
                else:
                    self.define.append('LITTLE_END',None)
            
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
                        tmpfilename = os.path.join(self.build_temp,sources[i][1:])
                        if os.path.isfile       (tmpfilename):
                            filename = tmpfilename
                        else:
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
    
        def build_extensions(self):
            # First, sanity-check the 'extensions' list
            
            for ext in self.extensions:
                ext.sources = self.substitute_sources(ext.name,ext.sources)
                
            self.check_extensions_list(self.extensions)
    
            for ext in self.extensions:
                log.info("%s :-> %s",ext.name,ext.sources)
                ext.sources = self.cython_sources(ext.sources, ext)
                self.build_extension(ext)
    
            
        def run(self):
            self.modifyDocScripts()
    
            for cmd_name in self.get_sub_commands():
                self.run_command(cmd_name)
    
            cython_options.annotate = True
            ori_build_ext.run(self)  # @UndefinedVariable
            
    
        def has_files(self):
            return self.distribution.has_files()
    
        def has_executables(self):
            return self.distribution.has_executables()
        
        sub_commands = [('build_files',has_files),
                        ('build_cexe', has_executables)
                        ] + \
                       ori_build_ext.sub_commands

except ImportError:
    from distutils.command import build_ext  # @UnusedImport
           


        