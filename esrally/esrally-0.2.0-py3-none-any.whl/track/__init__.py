from os.path import dirname, basename, isfile
import glob

# "Autodiscover" all available tracks
modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f)]
