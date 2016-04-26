import os
import pkg_resources as pkr

from shutil import copyfile
from ConfigParser import ConfigParser


def get_scry_dir():
    if 'SCRY_DIR' in os.environ:
        return os.environ['SCRY_DIR']
    else:
        return os.path.expanduser(os.path.join('~','Documents','SCRY'))


def get_conf():
    path = os.path.join(get_scry_dir(),'config.ini')
    pkr.ensure_directory(path)
    if not os.path.isfile(path):
        copyfile(pkr.resource_filename('scry',os.path.join('resources','config.default')),path)
    conf = ConfigParser()
    conf.read(path)
    return conf


def write_conf(conf):
    path = os.path.join(get_scry_dir(),'config.ini')
    pkr.ensure_directory(path)
    with open(path,'w') as f:
        conf.write(f)


def get_subdir(*args):
    d = os.path.expanduser(os.path.join(get_scry_dir(),*args))
    if not d.endswith(os.sep): d += os.sep
    pkr.ensure_directory(d)
    return d


## Subdirectories
#SERVICE_DIR  = get_subdir('Services')
#LOG_DIR      = get_subdir('Logs')

## Services
#NO_LOAD      = [mod.strip() for mod in CONF.get('Services','no-load').split('\n')]
#REMOTE_LOAD  = [mod.strip() for mod in CONF.get('Services','remote-load').split('\n')]

# App
#DEFAULT_RESPONSE_TYPE     = CONF.get('App','default-response-type')

#DEBUG        = make_bool(CONF.get('App','debug'))
#PORT         = int(CONF.get('App','port'))
#ALLOW_REMOTE = make_bool(CONF.get('App','allow-remote'))
#ALLOWED_IPS  = [ip.strip() for ip in CONF.get('App','ips').strip().split('\n')]