__all__ = ("__title__",
           "__summary__",
           "__uri__",
           "__version__",
           "__author__",
           "__email__",
           "__license__",
           "__copyright__", )


def __get_version():
    from os import path
    f = path.abspath(path.dirname(__file__))
    return (open(path.join(f, 'version.py')).read())


exec(__get_version())

__title__ = "psst"
__summary__ = "A python power system simulation toolbox"
__uri__ = "https://github.com/power-system-simulation-toolbox/psst"

__author__ = "Dheepak Krishnamurthy"
__email__ = "kdheepak89@gmail.com"

__license__ = "Revised BSD License"
__copyright__ = "Copyright 2016 Dheepak Krishnamurthy"

