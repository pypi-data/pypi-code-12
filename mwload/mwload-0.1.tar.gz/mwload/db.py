import os
import io
import shelve

from . import parse

header = b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="en">\n'
footer = b'</mediawiki>\n'

_DOTDIR = os.path.join(os.environ['HOME'], '.mwh')

def _dbdir(dbname):
    return os.path.join(_DOTDIR, dbname)

def _open(dbname):
    tmp = _dbdir(dbname)
    fp = open(os.path.join(tmp, 'dump.xml'), 'rb')
    idb = shelve.open(os.path.join(tmp, 'inc'))
    return fp, idb

def inc(filename):
    # Set up the dotfiles.
    with open(filename, 'rb') as fp:
        dbname = parse.dbname(fp)
    tmp = _dbdir(dbname)
    os.makedirs(tmp, exist_ok=True)
    dump_fn = os.path.join(tmp, 'dump.xml')
    if os.path.islink(dump_fn):
        os.remove(dump_fn)
    os.symlink(filename, dump_fn)

    fp, idb = _open(tmp)
    for k, v in parse.inc(fp):
        idb[k.decode('utf-8')] = v
    return idb

def read(dbname, title):
    '''
    Read by offset.
    '''
    fp, idb = _open(dbname)
    pos = idb[title]
    fp.seek(pos)

    x = header
    for line in fp:
        x += line
        if line == b'  </page>\n':
            break
    x += footer

    return parse.text(io.BytesIO(x))

def list(dbname):
    fp, idb = _open(dbname)
    return iter(idb)

def names():
    return tuple(os.listdir(_DOTDIR))
