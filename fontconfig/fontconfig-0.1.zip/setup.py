from setuptools import setup


def get_version(filename, varname="__version__"):
    glb = {}
    with open("fc.py") as fp:
        for line in fp:
            if varname in line:
                exec line in glb
                break
    return glb[varname]


setup(name="fontconfig",
      version=get_version("fc.py"),
      description="CFFI bindings for fontconfig",
      long_description=open("README").read(),
      author="Marco Giusti",
      author_email="marco.giusti@posteo.de",
      license="MIT",
      url="https://bitbucket.org/gm/fontconfig",
      zip_safe=False,
      py_modules=["fc"],
      cffi_modules=["fontconfig_cffi.py:ffi"],
      setup_requires=["cffi>=1.0.0"],
      install_requires=["cffi>=1.0.0", "enum34"],
      keywords=["fontconfig", "cffi"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries"
      ]
)
