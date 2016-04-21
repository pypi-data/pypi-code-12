import sys
from os          import listdir
from rdflib      import Namespace
from scry.config import get_conf, get_subdir, write_conf

BLAST           = Namespace('http://scry.rocks/blast/')

CONF = get_conf()
if 'scry_blast' not in CONF.sections():
    # Set up the default configuration
    CONF.add_section('scry_blast')
    CONF.set('scry_blast','bin_dir','UNKNOWN')
    CONF.set('scry_blast','db_dir', get_subdir('Services','BLAST','db'))
    CONF.set('scry_blast','default_db', 'UNKNOWN')
    CONF.set('scry_blast','cache_seqs','True')
    CONF.set('scry_blast','cache_dir', get_subdir('Services','BLAST','sequence_cache'))
    write_conf(CONF)
    print "\n  New configuration parameters added to SCRY's config.ini for the `scry_blast` service."
    print "  Remember to configure `bin_dir` and add at least one database to the appropriate directory"
    print "  before importing this service with SCRY!\n"
    sys.exit()

DATABASES = list()
for f in listdir(CONF.get('scry_blast','db_dir')):
    if f.endswith('.psq'):
        DATABASES.append(f[:-4])

DEFAULT_DB = CONF.get('scry_blast','default_db')
if DEFAULT_DB == 'UNKNOWN':
    DEFAULT_DB = DATABASES[0]