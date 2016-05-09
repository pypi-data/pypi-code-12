'''
Created on 6 oct. 2014

@author: coissac
'''

# try:
#     from setuptools.command.install import install as install_ori
# except ImportError:
#     from distutils.command.install import install as install_ori

from distutils.command.install import install as install_ori

class install(install_ori):
    
    def __init__(self,dist):
        install_ori.__init__(self, dist)
#        self.sub_commands.insert(0, ('build',lambda self: True))
        self.sub_commands.append(('install_sphinx',lambda self: self.distribution.serenity))
