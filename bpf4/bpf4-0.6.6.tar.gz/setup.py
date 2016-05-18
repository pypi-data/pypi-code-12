"""
BPF

A package implementing piece-wise interpolation functions in Cython
"""
from __future__ import print_function
from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext
import numpy as np
import os
import sys

USE_CYTHON = True  
COMPILE_PARALLEL = False

def get_version():
    d = {}
    with open("bpf4/version.py") as f:    
        code = f.read()
    exec(code, d)        
    version = d.get('__version__', (0, 0, 0))
    return ("%d.%d.%d" % version).strip()

if not os.path.exists("README.md"):
    long_description = ""
else:
    try:
        import pypandoc
        long_description = pypandoc.convert('README.md', 'rst')
    except (IOError, ImportError):
        print("Could not convert README to RST")
        long_description = open('README.md').read()
    
# ----------------------------------------------
# monkey-patch for parallel compilation
# ----------------------------------------------
def parallelCCompile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
    # those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build =  self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    # parallel code
    import multiprocessing
    import multiprocessing.pool
    N = multiprocessing.cpu_count()
    def _single_compile(obj):
        try: src, ext = build[obj]
        except KeyError: return
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
    list(multiprocessing.pool.ThreadPool(N).imap(_single_compile,objects))
    return objects

if COMPILE_PARALLEL:
    import distutils.ccompiler
    distutils.ccompiler.CCompiler.compile = parallelCCompile

cmdclass     = {}
ext_modules  = []
compile_args = [] 

if sys.platform == 'windows':
    compile_args += ["-march=i686"]  # This is needed in windows to compile cleanly

extra_link_args = compile_args 
versionstr = get_version()

metadata = {
    
    }

include_dirs = [
    np.get_include(),
    'bpf4'
]

ext_common_args = {
    'extra_compile_args': compile_args,
    'extra_link_args': extra_link_args, 
    'include_dirs': include_dirs
}

ext_modules += [
    Extension(
        "bpf4.core", 
        [ "bpf4/core.pyx" ], 
        **ext_common_args
        ),
    ]

cmdclass.update({ 'build_ext': build_ext })

setup(
    name = "bpf4",
    cmdclass = cmdclass,
    ext_modules = ext_modules,
    include_dirs = [np.get_include()],
    setup_requires = ['cython>=0.19', 'numpy>=1.7'],
    install_requires = ['numpy>=1.7'],
    packages = ['bpf4'],

    # metadata
    version          = versionstr,
    url              = 'https://github.com/gesellkammer/bpf4',
    download_url     = 'https://github.com/gesellkammer/bpf4', 
    author           = 'eduardo moguillansky',
    author_email     = 'eduardo moguillansky at gmail dot com',
    maintainer       = '',
    maintainer_email = '',
    long_description = long_description,
    description = "Pice-wise interpolation"
)

print("Version: %s" % versionstr)
print(long_description)
