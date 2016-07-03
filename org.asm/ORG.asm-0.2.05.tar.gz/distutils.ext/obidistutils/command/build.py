'''
Created on 20 oct. 2012

@author: coissac
'''

from distutils.command.build import build as ori_build
from obidistutils.serenity.checksystem import is_mac_system


class build(ori_build):
    
    def has_ext_modules(self):
        return self.distribution.has_ext_modules()
    
    def has_pidname(self):
        return is_mac_system()

    def has_doc(self):
        return True
    
    def has_littlebigman(self):
        return True
    
    try:
        from obidistutils.command.build_sphinx import build_sphinx  # @UnusedImport

        sub_commands = [("littlebigman",has_littlebigman),
                         ('pidname',has_pidname)
                       ] \
                       + ori_build.sub_commands + \
                       [('build_sphinx',has_doc)]
    except ImportError:
        sub_commands = [("littlebigman",has_littlebigman),
                         ('pidname',has_pidname)
                       ] \
                       + ori_build.sub_commands
        
