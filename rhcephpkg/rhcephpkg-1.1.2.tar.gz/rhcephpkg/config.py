import os
from six.moves import configparser


class Config(object):
    def __init__(self, confdir=None):


def get(section, option, confdir=os.environ['HOME']):
    """ Return the value from ConfigParser. If it does not exist, exit with a
    simple message. """
    # It feels a little ineffecient to instantiate a new RawConfigParser on
    # each call, but this is an old-style object on Python 2, so I don't know
    # how to subclass it (to override parser.get()), which would probably be
    # more elegant.
    parser = configparser.RawConfigParser()
    path = os.path.join(confdir, '.rhcephpkg.conf')
    import pdb
    pdb.set_trace()
    parser.read(path)
    try:
        return parser.get(section, option)
    except configparser.Error as err:
        raise SystemExit('Problem parsing ~/.rhcephpkg.conf: %s', err.message)
