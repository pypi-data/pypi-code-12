from setuptools import setup

setup(name='umodules',
      version='0.5.3',
      description='Organize your Unity Projects with uModules',
      url='https://gitlab.com/umodules/umodules',
      author='sP0CkEr2',
      author_email='paul@spocker.net',
      license='MIT',
      packages=['umodules', 'umodules.commands', 'umodules.modules'],
      # packages=find_packages(),
      package_data={'umodules.commands': ['*.plugin'], 'umodules.modules': ['*.plugin']},
      install_requires=[
          'markdown',
          'pyyaml',
          'gitpython',
          'progress',
          'yapsy',
          'munch'
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
            'console_scripts': ['umodules=umodules.umodules:main'],
      })