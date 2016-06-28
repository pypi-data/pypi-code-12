"""
A simple api for querying the version of the components used by hackedit.

Note that not all 3rd party libraries are shown, this is because:

    - those 3rd party libs are included in a zip archive
    - we do not know anything about 3rd party libs needed by
      plugins.
"""
from hackedit.app.versions import get_versions as get_versions_raw


def get_versions():
    """
    Returns a dict of versions. Keys are the names of the components and values
    are the version numbers.
    """
    raw_versions = get_versions_raw()

    return {
        'HackEdit': raw_versions['hackedit'],
        'PyQt5': raw_versions['qt_api_ver'],
        'Python':  '%s (%sbits)' % (
            raw_versions['python'], raw_versions['bitness']),
        'pyQode': '.'.join(raw_versions['pyqode.core'].split('.')[:2])
    }


def versions_str():
    strings = []
    for k, v in sorted(get_versions().items(), key=lambda x: x[0]):
        strings.append('%s: %s' % (k, v))
    return '\n'.join(strings)


if __name__ == '__main__':
    print(versions_str())
