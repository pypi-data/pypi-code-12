from setuptools import setup
from os import path

# Use README as the long description
project_dir = path.abspath(path.dirname(__file__))
with open(path.join(project_dir, 'README.rst')) as f:
        long_description = f.read()

setup(name='bblame',
      version='0.1.5',
      description='An ncurses app for viewing git file history',
      long_description=long_description,
      url='https://bitbucket.org/niko333/betterblame',
      author='Niko O',
      author_email='oliveira.n3@gmail.com',
      license='MIT',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Build Tools',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3'],
      keywords=['better git blame history curses ncurses'],
      packages=['betterblame'],
      install_requires=[
          'texteditpad',
          'future',
          'sh',
      ],
      scripts=['bblame'],
      # entry_points={
      #     'console_scripts': [
      #         'bblame = bblame.bblame:main',
      #     ]
      # },
      zip_safe=False)
