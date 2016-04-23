from setuptools import setup

setup(name='rabbit-backup',
      version='0.0.5',
      description='backup local files to dropbox. rabbit_backup_to_dropbox will remove local/remote files after verified based on setting. ',
      author='Guoliang Li',
      author_email='dev@liguoliang.com',
      url='http://guoliang-dev.github.io/rabbit-backup',
      packages=['rabbit_backup'],
      scripts=['scripts/rabbit-backup.py'],
      license='Apache Software License',
      install_requires=['dropbox', 'python-dateutil']
     )