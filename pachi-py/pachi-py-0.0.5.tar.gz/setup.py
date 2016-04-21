from distutils.command.build import build as DistutilsBuild
from setuptools import setup, Extension
import subprocess
import numpy
import os

with open(os.path.join(os.path.dirname(__file__), 'pachi_py/package_data.txt')) as f:
    package_data = [line.rstrip() for line in f.readlines()]


# For building Pachi as a library
class BuildLibPachi(DistutilsBuild):
    def run(self):
        try:
            subprocess.check_call("cd pachi_py; mkdir -p build && cd build && cmake ../pachi && make -j4", shell=True)
        except subprocess.CalledProcessError, e:
            print("Could not build pachi-py: %s" % e)
            raise
        DistutilsBuild.run(self)

ext = Extension(
    name="pachi_py.cypachi",
    sources=["pachi_py/cypachi.pyx", "pachi_py/goutil.cpp"],
    language="c++",
    include_dirs=[numpy.get_include(), "pachi_py/pachi"],
    libraries=["pachi"],
    library_dirs=["pachi_py/build/lib"], # this is the output dir of BuildLibPachi
    extra_compile_args=["-std=c++11"],
)

setup(name='pachi-py',
      version='0.0.5',
      description='Python bindings to Pachi',
      url='https://github.com/rl-gym/pachi-py',
      author='OpenAI',
      author_email='info@openai.com',
      packages=['pachi_py'],
      package_data={'pachi_py': package_data},
      cmdclass={'build': BuildLibPachi},
      install_requires=['numpy'],
      tests_require=['nose2'],
      classifiers=['License :: OSI Approved :: GNU General Public License v2 (GPLv2)'],
      ext_modules=[ext],
      extra_objects = ["pachi_py/build/lib/libpachi.so"]
)
