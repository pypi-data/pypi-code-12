from setuptools import setup


setup(name='ttv',
      version='0.0.1',
      description='A command line tool and a python library for test, train, validation set splitting',
      author='Sam Coope',
      author_email='sam.j.coope@gmail.com',
      url='https://github.com/coopie/ttv',
      download_url='https://github.com/coopie/ttv/archive/master.zip',
      license='MIT',
      install_requires=['docopt', 'pyyaml'],
      py_modules=['ttv']
)
