'''
Created on 6 oct. 2014

@author: coissac
'''

try:
    from setuptools.command.install import install as install_ori
    has_setuptools=True
except ImportError:
    from distutils.command.install import install as install_ori
    has_setuptools=False

from distutils import log

class install(install_ori):
    
    def __init__(self,dist):
        install_ori.__init__(self, dist)
        self.sub_commands.insert(0, ('build',lambda self: True))
        self.sub_commands.append(('install_sphinx',lambda self: self.distribution.serenity))

    def run(self):
        log.info('\n\nRunning obidistutils install process\n\n')
        install_ori.run(self)
