#!/usr/bin/env python

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from subprocess import call

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

import versioneer


# Add custom build commands for versioneer
cmdclass = versioneer.get_cmdclass()

class ImmunioBuild(build_ext):
    def run(self):
        """ First pre-build the require static library:

            "immunio/lua-hooks/ext/luajit/src/libluajit.a"
        """
        args = ["make", "-C", "immunio/lua-hooks", "ext/luajit/src/libluajit.a"]
        self.execute(call, [args], "Building libluajit.a")

        args = ["make", "-C", "immunio/lua-hooks", "libimmunio.a"]
        self.execute(call, [args], "Building libimmunio.a")

        build_ext.run(self)

# Add the custom `build_ext` class.
cmdclass["build_ext"] = ImmunioBuild


setup(name='immunio',
      version=versioneer.get_version(),
      description='Immunio agent library',
      author='Immunio',
      author_email='contact@immun.io',
      url='https://www.immun.io',
      packages=find_packages(exclude=["tests", "tests.*"]),
      include_package_data=True,
      install_requires=['msgpack-python'],
      use_2to3=True,
      ext_modules=[Extension(
          b'immunio.deps.lupa._lupa',
          sources=[
              b'immunio/deps/lupa/_lupa.c',
          ],
          extra_compile_args=[b'-DLUA_USE_APICHECK',
                              b'-DLUAJIT',
                              b'-Dlua_assert=assert',
                              b'-O3',
                              b'-fPIC'],
          # The order of the following libraries is important.
          # The symbol lj_lib_load is defined in both and we
          # need to have our version picked up.
          extra_objects=[
                        b'immunio/lua-hooks/libimmunio.a',
                        b'immunio/lua-hooks/ext/luajit/src/libluajit.a'
          ],
          include_dirs=[b'immunio/lua-hooks/ext',
                        b'immunio/lua-hooks/ext/luajit/src/'],
      )],
      classifiers=[
          "Framework :: Django",
          "Framework :: Flask",
          "Framework :: Pyramid",
          "Intended Audience :: Developers",
          "License :: Other/Proprietary License",
          "Topic :: Security",
      ],
      cmdclass=cmdclass,
)
