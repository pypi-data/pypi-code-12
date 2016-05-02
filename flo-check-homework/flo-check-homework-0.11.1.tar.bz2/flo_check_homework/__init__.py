import collections
_VersionInfo = collections.namedtuple(
    "VersionInfo", ("major", "minor", "micro", "releasesuffix"))

class VersionInfo(_VersionInfo):
    def __str__(self):
        res = ".".join( ( str(elt) for elt in self[:3] ) )
        if self.releasesuffix:
            res += self.releasesuffix
        return res

    def __repr__(self):
        return "{0}.{1}".format(__name__, _VersionInfo.__repr__(self))

version_info = VersionInfo(0, 11, 1, "")
__version__ = str(version_info)

del collections
