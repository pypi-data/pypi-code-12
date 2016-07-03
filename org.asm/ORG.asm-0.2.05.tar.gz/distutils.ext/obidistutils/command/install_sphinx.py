'''
Created on 10 mars 2015

@author: coissac
'''
from distutils.core import Command
import os.path
import glob

class install_sphinx(Command):
    '''
    Install the sphinx documentation
    '''
    
    description = "Install the sphinx documentation in serenity mode"

    boolean_options = ['force', 'skip-build']


    def initialize_options (self):
        self.install_doc = None
        self.build_dir = None

    def finalize_options (self):
        self.set_undefined_options('build_sphinx', ('build_dir', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_scripts', 'install_doc'))

    def run (self):
        if self.distribution.serenity:
            self.install_doc = os.path.join(self.install_doc,"../export/share")
            self.install_doc=os.path.abspath(self.install_doc)
            self.mkpath(self.install_doc)
            self.mkpath(os.path.join(self.install_doc,'html'))
            outfiles = self.copy_tree(os.path.join(self.build_dir,'html'),  # @UnusedVariable
                                      os.path.join(self.install_doc,'html'))
                
            self.mkpath(os.path.join(self.install_doc,'man','man1'))
            outfiles = self.copy_tree(os.path.join(self.build_dir,'man'),  # @UnusedVariable
                                      os.path.join(self.install_doc,'man','man1'))

            for epub in glob.glob(os.path.join(self.build_dir,'epub/*.epub')):
                self.copy_file(os.path.join(epub), 
                               os.path.join(self.install_doc,os.path.split(epub)[1]))
            
    def get_outputs(self):
        directory=os.path.join(self.install_doc,'html')
        files = [os.path.join(self.install_doc,'html', f) 
                 for dp, dn, filenames in os.walk(directory) for f in filenames]  # @UnusedVariable
        
        directory=os.path.join(self.build_dir,'man')
        files.append(os.path.join(self.install_doc,'man','man1', f) 
                 for dp, dn, filenames in os.walk(directory) for f in filenames)  # @UnusedVariable

        directory=os.path.join(self.build_dir,'epub')
        files.append(os.path.join(self.install_doc, f) 
                 for dp, dn, filenames in os.walk(directory)  # @UnusedVariable
                 for f in glob.glob(os.path.join(dp, '*.epub')) )
        
        return files
        