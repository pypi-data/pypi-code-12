from pbr import util

from arya.build.version import get_version


def apply_options(dist, attrs):
    for key, val in attrs.items():
        if hasattr(dist.metadata, 'set_' + key):
            getattr(dist.metadata, 'set_' + key)(val)
        elif hasattr(dist.metadata, key):
            setattr(dist.metadata, key, val)
        elif hasattr(dist, key):
            setattr(dist, key, val)
        else:
            msg = 'Unknown distribution option: %s' % repr(key)
            warnings.warn(msg)


def get_attrs():
    attrs = util.cfg_to_args()
    attrs['version'] = get_version()
    return attrs


def arya(dist, attr, value):
    attrs = get_attrs()
    apply_options(dist, attrs)
