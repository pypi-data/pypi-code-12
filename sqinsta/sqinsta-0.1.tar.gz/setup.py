from setuptools import setup

setup(name='sqinsta',
      version='0.1',
      description='Download Insagram profile photos from command line',
      url='https://github.com/saqirzzq/instaPy',
      author='Saqib Razzaq',
      author_email='saqi.cb@gmail.com',
      license='MIT',
      install_requires = ['beautifulsoup4>=4.4','requests'],
      packages=['sqinsta'],
      entry_points={
          'console_scripts': [
              'sqinsta = sqinsta.__init__:main'
          ]
      },
      zip_safe=False)