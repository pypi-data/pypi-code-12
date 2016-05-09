'''
Created on 20 oct. 2012

@author: coissac
'''

from os import path
import os.path
import glob
import sys

# try:
#     from setuptools.extension import Extension
# except ImportError:
#     from distutils.extension import Extension

from distutils.extension import Extension

from obidistutils.serenity.checkpackage import  install_requirements,\
                                                check_requirements, \
                                                RequirementError
                                                
from obidistutils.serenity.rerun import enforce_good_python
from obidistutils.serenity.rerun import rerun_with_anothe_python
from distutils import log

from obidistutils.dist import Distribution
from obidistutils.serenity import is_serenity
 
 
def findPackage(root,base=None):
    modules=[]
    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
        modules.append('.'.join(base+[module]))
        modules.extend(findPackage(path.join(root,module),base+[module]))
    return modules
    
def findCython(root,base=None,pyrexs=None):
    setupdir = os.path.dirname(sys.argv[0])
    pyrexs=[]

    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
                       
                
        for pyrex in glob.glob(path.join(root,module,'*.pyx')):
            pyrexs.append(Extension('.'.join(base+[module,path.splitext(path.basename(pyrex))[0]]),
                                    [pyrex]
                                    )
                          )
            try:
                cfiles = os.path.splitext(pyrex)[0]+".cfiles"
                cfilesdir = os.path.dirname(cfiles)
                cfiles = open(cfiles)
                cfiles = [os.path.relpath(os.path.join(cfilesdir,y),setupdir).strip() 
                          if y[0] !='@' else y.strip()
                          for y in cfiles]
                
                log.info("Cython module : %s",cfiles)   
                incdir = set(os.path.dirname(x) for x in cfiles if x[-2:]==".h")
                cfiles = [x for x in cfiles if x[-2:]==".c"]                
                pyrexs[-1].sources.extend(cfiles)
                pyrexs[-1].include_dirs.extend(incdir)
                pyrexs[-1].extra_compile_args.extend(['-msse2',
                                                      '-Wno-unused-function',
                                                      '-Wmissing-braces',
                                                      '-Wchar-subscripts'])
                
            except IOError:
                pass
            
        pyrexs.extend(findCython(path.join(root,module),base+[module]))
    return pyrexs
    

def rootname(x):
    return os.path.splitext(x.sources[0])[0]


def prepare_commands():
    from obidistutils.command.build import build
    from obidistutils.command.littlebigman import littlebigman
#    from obidistutils.command.serenity import serenity
    from obidistutils.command.build_cexe import build_cexe
    from obidistutils.command.build_ext import build_ext
    from obidistutils.command.build_ctools import build_ctools
    from obidistutils.command.build_files import build_files
    from obidistutils.command.build_scripts import build_scripts
    from obidistutils.command.install_scripts import install_scripts
    from obidistutils.command.install_sphinx import install_sphinx
    from obidistutils.command.install import install
    from obidistutils.command.pidname import pidname
    from obidistutils.command.sdist import sdist
    
        
    
    COMMANDS = {'build':build,
#                'serenity':serenity,
                'littlebigman':littlebigman,
                'pidname':pidname,
                'build_ctools':build_ctools, 
                'build_files':build_files,
                'build_cexe':build_cexe, 
                'build_ext': build_ext,
                'build_scripts':build_scripts, 
                'install_scripts':install_scripts,
                'install_sphinx':install_sphinx,
                'install':install,
                'sdist':sdist}
    
#     try:
#         from setuptools.commands import egg_info
#         COMMANDS['egg_info']=egg_info
#     except ImportError:
#         pass
    try:
        from obidistutils.command.build_sphinx import build_sphinx
        COMMANDS['build_sphinx']=build_sphinx
    except ImportError:
        pass

    return COMMANDS


CTOOLS =[]
CEXES  =[]
FILES  =[]

def setup(**attrs):
    
    log.set_threshold(log.INFO)
    
    minversion      = attrs.get("pythonmin",'3.4')
    maxversion      = attrs.get('pythonmax',None)    
    fork            = attrs.get('fork',False)
    requirementfile = attrs.get('requirements','requirements.txt')

    try:
        del attrs['pythonmin']
    except KeyError:
        pass

    try:
        del attrs['pythonmax']
    except KeyError:
        pass

    try:
        del attrs['fork']
    except KeyError:
        pass

    try:
        del attrs['requirements']
    except KeyError:
        pass
    
    if is_serenity():
    
        
        enforce_good_python(minversion, maxversion, fork)
        
        if (install_requirements(requirementfile)):
            rerun_with_anothe_python(sys.executable,minversion,maxversion,fork)
        
    
        try:
            check_requirements(requirementfile)
        except RequirementError as e :
            log.error(e)                                   
            sys.exit(1)
        
    if 'distclass' not in attrs:
        attrs['distclass']=Distribution

    if 'python_src' not in attrs:
        SRC = 'python'
    else:
        SRC = attrs['python_src']
        del(attrs['python_src'])
    
    if 'scripts' not in attrs:
        attrs['scripts'] = glob.glob('%s/*.py' % SRC)

    if 'package_dir' not in attrs:
        attrs['package_dir'] = {'': SRC}

    if 'packages' not in attrs:
        attrs['packages'] = findPackage(SRC)
    
    if 'cmdclass' not in attrs:
        attrs['cmdclass'] = prepare_commands()

    if 'ctools' not in attrs:
        attrs['ctools'] = CTOOLS
    
    if 'executables' not in attrs:
        attrs['executables'] = CEXES
        
    if 'files' not in attrs:
        attrs['files'] = FILES
        
    if 'sse' not in attrs:
        attrs['sse']=None
        
    if 'serenity' not in attrs:
        attrs['serenity']=False
    
    EXTENTION=findCython(SRC)
    
    if 'ext_modules' not in attrs:
        attrs['ext_modules'] = EXTENTION
        
#     try:
#         from setuptools.core import setup as ori_setup
#     except ImportError:
#         from distutils.core import setup as ori_setup

    from distutils.core import setup as ori_setup
    
    ori_setup(**attrs)
