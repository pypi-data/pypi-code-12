from os import path

package_dir = path.dirname(path.abspath(__file__))
with open(path.join(package_dir, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()
