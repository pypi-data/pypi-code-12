import numpy
import os
import shutil
import subprocess
import tempfile

from setuptools import setup
from distutils.extension import Extension
from Cython.Build import cythonize


def check_for_openmp():
    # Create a temporary directory
    tmpdir = tempfile.mkdtemp()
    curdir = os.getcwd()
    exit_code = 1

    if os.name == 'nt':
        return False

    try:
        os.chdir(tmpdir)

        # Get compiler invocation
        compiler = os.getenv('CC', 'cc')

        # Attempt to compile a test script.
        # See http://openmp.org/wp/openmp-compilers/
        filename = r'test.c'
        fileh = open(filename, 'w', 1)
        fileh.write(
            "#include <omp.h>\n"
            "#include <stdio.h>\n"
            "int main() {\n"
            "#pragma omp parallel\n"
            "printf(\"Hello from thread %d, nthreads %d\\n\", omp_get_thread_num(), omp_get_num_threads());\n"  # NOQA
            "}\n"
        )
        with open(os.devnull, 'w') as fnull:
            exit_code = subprocess.call([compiler, '-fopenmp', filename],
                                        stdout=fnull, stderr=fnull)

        # Clean up
        fileh.close()
    finally:
        os.chdir(curdir)
        shutil.rmtree(tmpdir)

    return exit_code == 0

if check_for_openmp() is True:
    omp_args = ['-fopenmp']
else:
    omp_args = None

ext_modules = (
    Extension(
        "galanyl.radial_flux_analyzer.line_circle_intercepts",
        ["galanyl/radial_flux_analyzer/line_circle_intercepts.pyx"]),
    Extension(
        "galanyl.cython_extensions.dispersion",
        ["galanyl/cython_extensions/dispersion.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=omp_args,
        extra_link_args=omp_args),
    Extension(
        "galanyl.cython_extensions.cic_density",
        ["galanyl/cython_extensions/cic_density.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=omp_args,
        extra_link_args=omp_args),
    Extension(
        "galanyl.cython_extensions.scale_height",
        ["galanyl/cython_extensions/scale_height.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=omp_args,
        extra_link_args=omp_args),
    Extension(
        "galanyl.cython_extensions.windowed_sum",
        ["galanyl/cython_extensions/windowed_sum.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=omp_args,
        extra_link_args=omp_args),
)

setup(
    name="galanyl",
    version="0.1.7",
    author="Nathan Goldbaum, John Forbes",
    author_email="nathan12343@gmail.com",
    url="https://bitbucket.org/ngoldbaum/galaxy_analysis",
    packages=[
        'galanyl',
        'galanyl.radial_flux_analyzer',
        'galanyl.plotting',
        'galanyl.rotation_curve',
        'galanyl.cython_extensions',
    ],
    install_requires=[
        'numpy',
        'scipy',
        'cython',
        'matplotlib',
        'numexpr',
        'six',
        'h5py',
        'scikit-image'
    ],
    ext_modules=cythonize(ext_modules),
)
