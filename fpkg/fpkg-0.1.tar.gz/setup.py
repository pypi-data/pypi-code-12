from setuptools import find_packages, setup
setup(name="fpkg",
      version="0.1",
      description="A pkg utility",
      author="amoschang",
      author_email='amos@it.org',
      platforms=["any"],  # or more specific, e.g. "win32", "cygwin", "osx"
      license="MIT",
      url="http://github.com/ewencp/foo",
      packages=find_packages(),
      zip_safe=False)
