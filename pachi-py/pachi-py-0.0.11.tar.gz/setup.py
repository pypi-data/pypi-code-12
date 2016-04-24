from distutils.command.build import build as DistutilsBuild
from setuptools import setup, Extension
import subprocess

# We actually want to also include numpy's include dirs. However,
# numpy may not be installed at setup.py load time. So we set up a
# stub include array, and then modify it before the build begins.
include_dirs = ["pachi_py/pachi"]

# For building Pachi as a library
PACHI_BUILD_TYPE = 'Release'
class BuildLibPachi(DistutilsBuild):
    def run(self):
        global include_dirs

        import numpy
        include_dirs += numpy.get_include()
        try:
            subprocess.check_call("cd pachi_py; mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE={} ../pachi && make -j4".format(PACHI_BUILD_TYPE), shell=True)
        except subprocess.CalledProcessError, e:
            print("Could not build pachi-py: %s" % e)
            raise
        DistutilsBuild.run(self)

# Cython recommands checking in the Cython-generated C files
# (cf. http://stackoverflow.com/a/19138055).
# After changing pachi_py/cypachi.pyx, recompile using:
#
#     $ cython --cplus pachi_py/cypachi.pyx
#
ext = Extension(
    name="pachi_py.cypachi",
    sources=["pachi_py/cypachi.cpp", "pachi_py/goutil.cpp"],
    language="c++",
    include_dirs=include_dirs,
    libraries=["pachi"],
    library_dirs=["pachi_py/build/lib"], # this is the output dir of BuildLibPachi
    extra_compile_args=["-std=c++11"],
)

setup(name='pachi-py',
      version='0.0.11',
      description='Python bindings to Pachi',
      url='https://github.com/rl-gym/pachi-py',
      author='OpenAI',
      author_email='info@openai.com',
      packages=['pachi_py'],
      cmdclass={'build': BuildLibPachi},
      setup_requires=['numpy'],
      install_requires=['numpy'],
      tests_require=['nose2'],
      classifiers=['License :: OSI Approved :: GNU General Public License v2 (GPLv2)'],
      ext_modules=[ext],
      include_package_data=True,
)
