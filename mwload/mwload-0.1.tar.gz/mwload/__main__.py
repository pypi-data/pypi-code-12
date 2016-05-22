import os
import sys
import horetu

from . import db

dbnames = db.names()

def inc(filename):
    '''
    Generate a table of contents.

    :param filename: An XML MediaWiki dump file
    '''
    idb = db.inc(filename)
    sys.stdout.write('Found %d articles\n' % len(idb))

def ls(dbname: dbnames):
    '''
    List articles in a database.

    :param dbname: Database name
    '''
    for i in db.list(dbname):
        sys.stdout.buffer.write((i + '\n').encode('utf-8'))

def read(title, dbname: dbnames=None):
    '''
    Read an article.

    :param title: Article title
    :param dbname: Database name
    '''
    if dbname:
        xs = (dbname,)
    else:
        xs = dbnames

    for x in xs:
        try:
            text = db.read(x, title)
        except KeyError:
            pass
        else:
            sys.stdout.buffer.write(text.encode('utf-8'))
            break
    else:
        sys.stderr.write('No article with title "%s"\n' % title)
        sys.exit(1)

horetu.horetu([inc, ls, read])
