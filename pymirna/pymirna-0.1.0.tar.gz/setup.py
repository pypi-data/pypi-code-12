# from distutils.core import setup
# from distutils.cmd import Command
#
# class TestCommand(Command):
#     user_options = []
#
#     def initialize_options(self):
#         pass
#     def finalize_options(self):
#         pass
#     def run(self):
#         pass
#
# setup(name='pymirna',
#       version='0.1',
#       description="pymirna: The Pythonic microRNA Library",
#       packages=['pymirna','pymirna.SeqIO'],
#       cmdclass={
#           'test': TestCommand
#       }
# )


#from distutils.core import setup
from setuptools import setup
from distutils.cmd import Command

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        pass

setup(name='pymirna',
      version='0.1.0',
      description="pymirna: The Pythonic microRNA Library",
      author='K. Somboonviwat',
      author_email='kulwadee.a@gmail.com',
      license='MIT',
      packages=['pymirna','pymirna.UI','pymirna.Utility'],
      install_requires=[
      'SIP', 'PyQt5',
      ],
      cmdclass={
          'test': TestCommand
      }
)
