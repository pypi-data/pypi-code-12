from setuptools import setup

setup(name='paybook',
      version='0.3',
      description='Paybook Python Sync SDK',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
         'Topic :: Text Processing :: Linguistic',
      ],
      keywords='Financial Processing Banks Tax',
      url='https://github.com/Paybook/sync-py.git',
      author='Hugo Ochoa',
      author_email='hugo@paybook.com',
      license='MIT',
      packages=['paybook'],
      zip_safe=False
)#End of setup

# Pending: json, sqlite3, flask.ext.cors import CORS, cross_origin
# sudo python setup.py install

