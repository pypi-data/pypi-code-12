from setuptools import setup

setup(
    name='rapper',
    version='0.1.1',
    py_modules=['first'],
    author='Syam Sasi',
    author_email='syamsasi99@gmail.com',
    entry_points='''
          [console_scripts]
          first=first:cli
          '''
      
)
