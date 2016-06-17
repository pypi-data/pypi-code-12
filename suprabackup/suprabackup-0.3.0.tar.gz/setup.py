"""
Setup script for suprabackup

"""

from setuptools import setup
from setuptools import find_packages


def readme():
    """
    Extracts contents from README.md

    """
    with open('README.md') as r:
        return r.read()


def requirements():
    """
    Fetch requirements from requirements.txt

    """
    with open('requirements.txt') as req:
        return req.read().splitlines()


setup(name='suprabackup',
      version='0.3.0',
      description='Suprabackup is a tool to automate xtrabackup database backups',
      long_description=readme(),
      license='MIT',
      url='https://github.com/quanta-computing/suprabackup',
      author="Matthieu 'Korrigan' Rosinski",
      author_email='mro@quanta-computing.com',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python',
          'License :: OSI Approved :: MIT License',
          'Topic :: Database',
          'Topic :: System :: Archiving :: Backup',
      ],
      packages=find_packages(),
      entry_points = {
        'console_scripts': [
            'suprabackup-send = suprabackup.scripts.send:main',
            'suprabackup-receive = suprabackup.scripts.receive:main',
            'suprabackup-verify = suprabackup.scripts.verify:main',
            'suprabackup-purge = suprabackup.scripts.purge:main',
            'suprashell = suprabackup.scripts.shell:main'
        ],
      },
      install_requires=requirements(),
  )
