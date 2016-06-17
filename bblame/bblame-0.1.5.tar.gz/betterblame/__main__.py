"""A main file for executing bblame from within the package without deploying
bblame as a binary or with distutils.
e.g. from root of the project dir: python -m betterblame"""
from .bblame import main
main()
