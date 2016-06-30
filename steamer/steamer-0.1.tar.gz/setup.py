from setuptools import setup

setup(name='steamer',
      version='0.1',
      description='Do things when files change',
      author='martylookalike',
      author_email='martylookalike@users.noreply.github.com',
      packages=['steamer'],
      keywords=['testing','task','tasks'],
      url = 'https://github.com/martylookalike/steamer',
      download_url = 'https://github.com/martylookalike/steamer/tarball/0.1',
      entry_points={
        'console_scripts': [
            'steamer = steamer.steamer:main'
        ]
      }
      )
