"""
Copyright: 2016 Saito Tsutomu
License: Python Software Foundation License
"""
import paramiko, os, re, sys, time, click
import digitalocean as do

class _Manager(do.Manager):
    def __init__(self):
        self.token = os.environ.get('DIOC_TOKEN')
        self.default_sshkey = os.environ.get('DIOC_DEFAULT_SSHKEY')
        self.default_size = os.environ.get('DIOC_DEFAULT_SIZE', '512mb')
        self.default_region = os.environ.get('DIOC_DEFAULT_REGION', 'sgp1')
        super().__init__(token=self.token)

def ssh_key_id(name=None):
    if not name:
        name = _manager.default_sshkey
    for sk in _manager.get_all_sshkeys():
        if sk.name == name:
            return sk.id
    return None

def image_id(name, private=False):
    for im in _manager.get_images(private):
        if im.name == name:
            return im.id

def droplet_id(name):
    for dr in _manager.get_all_droplets():
        if dr.name == name:
            return dr.id

def droplet(name):
    id = droplet_id(name)
    return _manager.get_droplet(id)

def create_droplet(dr):
    try:
        dr.create()  
        dr.get_action(dr.action_ids[0]).wait()
        dr.load()
    except Exception as e:
        sys.stderr.write('%s\n' % e)

def Droplet(name, image=None, size=None, region=None,
            ssh_keys=None, no_create=False, **kwargs):
    if not image:
        image = _manager.get_image('899.17.0 (stable)').id
    else:
        image = image_id(image)
    dc = {'name': name, 'image': image}
    dc.update(kwargs)
    if not size:
        size = _manager.default_size
    if not region:
        region = _manager.default_region
    if not ssh_keys:
        ssh_keys = [ssh_key_id()]
    if size:
        dc['size'] = size
    if region:
        dc['region'] = region
    if ssh_keys:
        dc['ssh_keys'] = ssh_keys
    dr = do.Droplet(token=_manager.token, **dc)
    if not no_create:
        create_droplet(dr)
    return dr

def ssh_host(name):
    d = droplet(name)
    return '%s@%s' % (ssh_user(d), d.ip_address)

def ssh_file(file):
    m = re.match('(.*)(:.*)|(.*)', file)
    if not m:
        return file
    h, f1, f2 = m.groups()
    return ssh_host(h) + f1 if h else f2

def ssh_user(dr):
    return 'core' if dr.image['distribution'] == 'CoreOS' else 'root'

def ssh_client(dr, user=None, **kwargs):
    if not user:
        user = ssh_user(dr)
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ip = dr.ip_address
    for i in range(6):
        try:
            time.sleep(1)
            cli.connect(ip, username=user, **kwargs)
            return cli
        except:
            pass
    else:
        sys.stderr.write('paramiko.connect error\n')

@click.group()
def action():
    """Manage Droplet of DigitalOcean."""
    pass

def chng(s):
    a, b = s.split('=')
    return a, b.strip('"').replace(r'\n', '\n')

@action.command()
@click.argument('name')
@click.argument('image', default='899.17.0 (stable)')
@click.argument('options', nargs=-1)
def create(name, image, options):
    Droplet(name, image, **dict(chng(s) for s in options))

@action.command()
@click.argument('name')
def destroy(name):
    droplet(name).destroy()

@action.command()
@click.argument('name')
@click.argument('command', nargs=-1)
def ssh(name, command):
    print(ssh_host(name), ' '.join(command))
    os.system('ssh {} {}'.format(ssh_host(name), ' '.join(command)))

@action.command()
@click.argument('src')
@click.argument('dst')
def scp(src, dst):
    os.system('scp -r -o StrictHostKeyChecking=no {} {}'.format(ssh_file(src), ssh_file(dst)))

@action.command()
@click.argument('name')
def ip(name):
    print(droplet(name).ip_address)

@action.command()
@click.argument('type', default='droplet',
    type=click.Choice(['droplet', 'image', 'private', 'ssh', 'size', 'region']))
def list(type):
    if type=='droplet':
        for dr in _manager.get_all_droplets():
            print(dr.name)
    elif type=='image':
        for im in _manager.get_images():
            print(im.name)
    elif type=='private':
        for im in _manager.get_images(True):
            print(im.name)
    elif type=='ssh':
        for sk in _manager.get_all_sshkeys():
            print(sk.name)
    elif type=='size':
        for si in _manager.get_all_sizes():
            if si.available:
                print('{0.memory}mb {0.disk}GB {0.vcpus}CPU {0.price_monthly}$/mo'.format(si))
    elif type=='region':
        for rg in _manager.get_all_regions():
            print(rg.name)

action.add_command(create)
action.add_command(destroy)
action.add_command(ssh)
action.add_command(scp)
action.add_command(ip)
action.add_command(list)

_manager = _Manager()
