import os
from os.path import join as pjoin
from os import path
import platform
import sys

def python_version_check():
    if sys.version_info[0] != 2:
        print("-"*85)
        print("PySpace doesn't support python 3. Please use 'python2 setup.py install' to install")
        print("Also run your scripts using python2 or make python 2.7 your default python interpreter")
        print("-"*85)
        sys.exit()

python_version_check()

import numpy
from setuptools import find_packages, setup
from Cython.Distutils import Extension
from Cython.Distutils import build_ext

def find_in_path(name, path):
    "Find a file in a search path"
    #adapted fom http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/
    for dir in path.split(os.pathsep):
        binpath = pjoin(dir, name)
        if os.path.exists(binpath):
            return os.path.abspath(binpath)
    return None

#Implementation based on https://github.com/rmcgibbo/npcuda-example
def locate_cuda():
    """Locate the CUDA environment on the system
    Returns a dict with keys 'home', 'nvcc', 'include', and 'lib'
    and values giving the absolute path to each directory.
    Starts by looking for the CUDAHOME env variable. If not found, everything
    is based on finding 'nvcc' in the PATH.
    """
    if os.environ.get('USE_CUDA', '') == '0':
        print("-"*70)
        print("USE_CUDA set to 0. CUDA disabled.")
        print("-"*70)
        return False, False
    # first check if the CUDAHOME env variable is in use
    if 'CUDAHOME' in os.environ:
        home = os.environ['CUDAHOME']
        nvcc = pjoin(home, 'bin', 'nvcc')
    else:
        # otherwise, search the PATH for NVCC
        nvcc = find_in_path('nvcc', os.environ['PATH'])
        if nvcc is None:
            print("-"*70)
            print("CUDA not found. Compiling without CUDA")
            print("-"*70)
            return False, False
        home = os.path.dirname(os.path.dirname(nvcc))

    cudaconfig = {'home':home, 'nvcc':nvcc,
                  'include': pjoin(home, 'include')}

    if platform.machine() == 'x86_64':
        cudaconfig['lib'] = pjoin(home, 'lib' + '64')
    else:
         cudaconfig['lib'] = pjoin(home, 'lib')

    cudalib = 'lib'
    for k, v in cudaconfig.iteritems():
        if not os.path.exists(v):
            raise EnvironmentError('The CUDA %s path could not be located in %s' % (k, v))

    print("-"*70)
    print("Using CUDA.")
    print("-"*70)

    return cudaconfig, cudalib

CUDA, cudalib = locate_cuda()

def customize_compiler_for_nvcc(self):
    """inject deep into distutils to customize how the dispatch
    to gcc/nvcc works.

    If you subclass UnixCCompiler, it's not trivial to get your subclass
    injected in, and still have the right customizations (i.e.
    distutils.sysconfig.customize_compiler) run on it. So instead of going
    the OO route, I have this. Note, it's kindof like a wierd functional
    subclassing going on."""

    # tell the compiler it can processes .cu
    self.src_extensions.append('.cu')

    # save references to the default compiler_so and _comple methods
    default_compiler_so = self.compiler_so
    super = self._compile

    # now redefine the _compile method. This gets executed for each
    # object but distutils doesn't have the ability to change compilers
    # based on source extension: we add it.
    def _compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
        if os.path.splitext(src)[1] == '.cu':
            # use the cuda for .cu files
            self.set_executable('compiler_so', CUDA['nvcc'])
            # use only a subset of the extra_postargs, which are 1-1 translated
            # from the extra_compile_args in the Extension class
            postargs = extra_postargs['nvcc']
        else:
            postargs = extra_postargs['gcc']

        super(obj, src, ext, cc_args, postargs, pp_opts)
        # reset the default compiler_so, which we might have changed for cuda
        self.compiler_so = default_compiler_so

    # inject our redefined _compile method into the class
    self._compile = _compile


# run the customize_compiler
class custom_build_ext(build_ext):
    def build_extensions(self):
        customize_compiler_for_nvcc(self.compiler)
        build_ext.build_extensions(self)

def get_omp_flags():
    """Returns openmp flags if OpenMP is available.

    Implementation based on https://bitbucket.org/pysph/pysph

    """
    omp_compile_flags, omp_link_flags = ['-fopenmp'], ['-fopenmp']

    env_var = os.environ.get('USE_OPENMP', '')
    if env_var.lower() in ['0', 'false', 'n']:
        print("-"*70)
        print("OpenMP disabled. Enable using 'USE_OPENMP'")
        print("-"*70)
        return [], [], False

    from textwrap import dedent
    try:
        from Cython.Distutils import Extension
        from pyximport import pyxbuild
    except ImportError:
        print("Unable to import Cython, disabling OpenMP for now.")
        return [], [], False
    from distutils.errors import CompileError, LinkError
    import shutil
    import tempfile
    test_code = dedent("""
    from cython.parallel import parallel, prange, threadid
    cimport openmp
    def n_threads():
        with nogil, parallel():
            openmp.omp_get_num_threads()
    """)
    tmp_dir = tempfile.mkdtemp()
    fname = path.join(tmp_dir, 'check_omp.pyx')
    with open(fname, 'w') as fp:
        fp.write(test_code)
    extension = Extension(
        name='check_omp', sources=[fname],
        extra_compile_args=omp_compile_flags,
        extra_link_args=omp_link_flags,
    )
    has_omp = True
    try:
        mod = pyxbuild.pyx_to_dll(fname, extension, pyxbuild_dir=tmp_dir)
        print("-"*70)
        print("Using OpenMP.")
        print("-"*70)
    except CompileError:
        print("*"*70)
        print("Unable to compile OpenMP code. Not using OpenMP.")
        print("*"*70)
        has_omp = False
    except LinkError:
        print("*"*70)
        print("Unable to link OpenMP code. Not using OpenMP.")
        print("*"*70)
        has_omp = False
    finally:
        shutil.rmtree(tmp_dir)

    if has_omp:
        return omp_compile_flags, omp_link_flags, True
    else:
        return [], [], False

requires = ["cython", "numpy", "pyevtk"]

ext_modules = []

omp_compile_flags, omp_link_flags, use_omp = get_omp_flags()

if CUDA != False:
    ext_modules += [
            Extension(
                "pyspace.simulator",
                sources = ["src/kernels.cu", "src/pyspace.cpp", "pyspace/simulator.pyx"],
                library_dirs = [CUDA[cudalib]],
                libraries = ['cudart'],
                runtime_library_dirs=[CUDA[cudalib]],
                include_dirs = ["src", numpy.get_include(), CUDA['include']],
                extra_compile_args = {'gcc': omp_compile_flags,
                                        'nvcc': ['-arch=sm_20', '--ptxas-options=-v', \
                                        '-c', '--compiler-options', "'-fPIC'"]},
                extra_link_args = omp_link_flags,
                cython_compile_time_env = {'USE_CUDA': True},
                language="c++"
                )
            ]

    ext_modules += [
            Extension(
                "pyspace.planet",
                ["pyspace/planet.pyx"],
                include_dirs = [numpy.get_include()],
                extra_compile_args = {'gcc': omp_compile_flags},
                language="c++"
                )
            ]


    compiler = custom_build_ext

else:
    ext_modules += [
            Extension(
                "pyspace.simulator",
                ["src/pyspace.cpp", "pyspace/simulator.pyx"],
                include_dirs = ["src", numpy.get_include()],
                extra_compile_args = omp_compile_flags,
                extra_link_args = omp_link_flags,
                cython_compile_time_env = {'USE_CUDA': False},
                language="c++"
                )
            ]

    ext_modules += [
            Extension(
                "pyspace.planet",
                ["pyspace/planet.pyx"],
                include_dirs = [numpy.get_include()],
                extra_compile_args = omp_compile_flags,
                language="c++"
                )
            ]


    compiler = build_ext


setup(
        name="PySpace",
        author="PySpace developers",
        author_email="adityapb1546@gmail.com",
        description="A toolbox for galactic simulations.",
        url = "https://github.com/adityapb/pyspace",
        long_description = open('README.rst').read(),
        version="0.1.0",
        install_requires=requires,
        packages=find_packages(),
        ext_modules = ext_modules,
        cmdclass = {'build_ext': compiler},
        zip_safe = False
    )


