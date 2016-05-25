#!/usr/bin/env python
from __future__ import print_function

"""
Conventions:

* Each service has a dedicated *nix user
* Use systemd
* No sudo, use root account when run system command
"""
import contextlib
import os, fnmatch
import time
import random
import string
from tempfile import NamedTemporaryFile as _Temp

from fabric.api import *
import fabric.contrib.files as files
import fabric.context_managers as fab_context
import fabric.contrib.project as fab_project


class _X:
    """ Custom variables """
    app = None
    base_port = 7000
    n_instances = 2
    remote_path = '/home/'
    wait = 3
    excludes = ('.*', 'tmp', '__pycache__', '*.pyc', 'upload', 'cache')
    dirs = ['config', 'src', 'doc']


env.x = _X()


def pwd(base_file):
    _pwd = os.path.dirname(base_file)
    os.chdir(_pwd)


def with_root():
    env.user = 'root'


def rand(n=16):
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.digits
        ) for _ in range(n)
    )


@contextlib.contextmanager
def on_remote(path=''):
    with cd(os.path.join(env.x.remote_path, path)):
        yield


@contextlib.contextmanager
def venv(inside=''):
    with prefix('source {remote}/bin/activate'
                .format(remote=env.x.remote_path)), cd(env.x.remote_path + inside):
        yield


def up_tokit():
    'git clone --single-branch --branch master https://github.com/manhg/tokit.git'
    with on_remote('tokit'):
        run('git fetch')
        run('git reset --hard origin/master')


def sync(dirs=None):
    if dirs:
        dirs = dirs.split(',')
    else:
        dirs = env.x.dirs
    for d in dirs:
        fab_project.rsync_project(remote_dir=env.x.remote_path, local_dir=d, exclude=env.x.excludes)


def pack():
    """ (1) Pack source code and send to remote server """
    # Alternative: Use fab_project.upload
    release_path = env.x.remote_path + '/tmp/%s_release.tgz' % env.x.app
    # To get UID: remote_uid = run('id -u')
    with _Temp(delete=False, suffix='.tgz') as tmp:
        local('tar cf {temp} src config doc'.format(temp=tmp.name))
        put(tmp.name, release_path)
    with on_remote():
        if files.exists('rollback'):
            run('rm -Rf rollback')
        if files.exists('config'):
            run('rm -Rf config')
        if files.exists('src'):
            run('mv src rollback')
        run('tar --extract --no-same-owner --preserve-permissions --file {release}'
            .format(release=release_path))
        run('rm ' + release_path)


def backend(action='restart'):
    """ (3) Start services """
    with_root()
    systemd_reload()
    for instance in range(env.x.n_instances):
        run('systemctl {action} {app}@{port}.service'.format(
            action=action,
            app=env.x.app,
            port=env.x.base_port + instance))
        time.sleep(env.x.wait)


def config():
    """ (3) Link configs """
    with_root()
    with on_remote():
        for instance in range(env.x.n_instances):
            service_file = "/etc/systemd/system/multi-user.target.wants/{app}@{port}.service" \
                .format(app=env.x.app, port=env.x.base_port + instance)
            run("ln -s -f {path}/config/app@.service {dest}"
                .format(path=env.x.remote_path, dest=service_file))
        run('ln -s -f {path}/config/nginx.conf /etc/nginx/conf.d/{app}.conf'
            .format(app=env.x.app, path=env.x.remote_path))


def rollback():
    with on_remote():
        run('mv src src-fail && mv rollback src')
        backend('restart')


def deploy():
    static_link()
    doc_gen()
    sync()
    requirements()
    backend('restart')
    static_copy()


def requirements():
    """ (2) Update dependancies """
    with on_remote():
        if not files.exists('bin'):
            run('pyvenv .')
        with venv('/src'):
            run('pip3 install --upgrade -r requirements.txt')
            # TODO update DB


def ssh_setup(public_key='~/.ssh/id_rsa.pub'):
    """ (0) Create user, add SSH key, create folders """
    env.user = 'root'
    run('useradd %s' % env.x.app)
    run('mkdir -p /home/%s/{.ssh,tmp,shared,src}' % env.x.app)
    run('ssh-keygen -b 2048 -t rsa -f /home/%s/.ssh/id_rsa -q -N ""' % env.x.app)
    put(public_key, '/home/%s/.ssh/authorized_keys' % env.x.app)
    run('chown %s -R /home/%s' % (env.x.app, env.x.app))
    run('chmod 700 /home/%s' % env.x.app)


def ssl_cert():
    env.user = 'root'
    cmd = (
        'openssl req -nodes req -nodes -new -sha256 -newkey rsa:2048 '
        '-keyout /etc/nginx/cert/{app}.key -out /etc/nginx/cert/{app}.csr '
        '-subj "/C=JP/ST=/L=/O=S/OU=/CN="'
    )
    run(cmd.format(app=env.x.app))


def authorize_key(key=None):
    """ Add an user to access server """
    if key:
        run('cat "%s">> /home/%s/.ssh/authorized_keys' % (key, env.x.app))
    else:
        print("Please provide a SSH public key")


def static_copy():
    with_root()
    run('mkdir -p /var/www/{app}'.format(app=env.x.app))
    run('cp -R {path}/src/static /var/www/{app}/'.format(path=env.x.remote_path, app=env.x.app))
    run('chown -R nginx /var/www/{app}/'.format(path=env.x.remote_path, app=env.x.app))


def systemd_reload():
    with_root()
    run('systemctl daemon-reload')


def up_file(name):
    file_dir = os.path.dirname(name)
    rel = os.path.relpath(name, file_dir)
    print(put(name, os.path.join(env.x.remote_path, rel)))


def up_python():
    with_root()
    backend('restart')


def up_nginx():
    # Pitfall
    with_root()
    config()
    systemd_reload()
    run('nginx -t && systemctl reload nginx.service')


def nginx(action='restart'):
    with_root()
    # PITFALL: first start must be a restart, not reload
    run('nginx -t && systemctl ' + action + ' nginx.service')


def find_files(directory, patterns):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            for pattern in patterns:
                if fnmatch.fnmatch(basename, pattern):
                    yield (root, basename)


def pack_config():
    pass


def up_project():
    fab_project.rsync_project(
        remote_dir=env.x.remote_path, local_dir='src',
        upload=True, extra_opts='-a', exclude=('__pycache__'))


def doc_gen():
    with fab_context.lcd('doc'):
        local('make')


def doc():
    """ Generate and display document in browser"""
    doc_gen()
    with fab_context.lcd('doc'):
        local('cd _build/html && python3 -m http.server 7359 >/dev/null 2>&1 &')
        local('open http://localhost:7359/')


def pg_dump_schema(db=None):
    import getpass
    local_username = getpass.getuser()
    if not db:
        db = env.x.app
    local('pg_dump -s %s  > config/schema.sql' % db)
    local('sed -i s/{local}/{remote}/g config/schema.sql'.format(local=local_username, remote=env.x.app))


def pg_up_schema():
    with _Temp(suffix='.dat') as tmp:
        local(
            ("pg_dump --schema-only "
             "--no-owner --no-acl --no-privileges "
             "--format=c --compress=9 "
             "--file={temp} {db} ")
            .format(temp=tmp.name, db=env.x.app))
        remote_sql = '{path}/tmp/schema.dat'.format(path=env.x.remote_path)
        put(tmp.name, remote_sql)
        run('pg_restore --no-owner --no-acl -d {app} {sql}'.format(sql=remote_sql, app=env.x.app))
        run('rm {sql}'.format(sql=remote_sql))


def pg_up_data():
    with _Temp(suffix='.dat') as tmp:
        local(
            ("pg_dump --data-only "
             "--no-owner --no-acl --no-privileges "
             "--format=c --compress=9 "
             "--file={temp} {db} ")
            .format(temp=tmp.name, db=env.x.app))
        remote_sql = '{path}/tmp/data.dat'.format(path=env.x.remote_path)
        put(tmp.name, remote_sql)
        run('pg_restore --no-owner --no-acl -d {app} {sql}'.format(sql=remote_sql, app=env.x.app))
        run('rm {sql}'.format(sql=remote_sql))


def pg_setup():
    """
    Create random database and user with password on remote server
    and save credential into production.ini config file
    """
    passwd = rand()
    with open('config/production.ini', 'a') as f:
        lines = [
            '[postgres]',
            'dsn=user={app} dbname={app} password={passwd}'.format(app=env.x.app, passwd=passwd),
            'size=4'
        ]
        for line in lines:
            f.write(line + "\n")
    with_root()
    sql_file = '/tmp/' + rand() + '.sql'
    with _Temp(suffix='.sql') as tmp:
        with open(tmp.name, 'w') as f:
            sql = """
                CREATE USER {app} WITH PASSWORD '{passwd}';
                CREATE DATABASE {app};
                GRANT ALL PRIVILEGES ON DATABASE {app} TO {app}
                """.format(passwd=passwd, app=env.x.app)
            f.write(sql)
            f.flush()
            put(tmp.name, sql_file)
    with on_remote('/tmp'):
        run("""su postgres -c 'cat {sql_file} | psql template1' """.format(sql_file=sql_file))
        run('rm ' + sql_file)


def static_link():
    """ Collect static files by symbolic links """
    original_dir = 'src'
    link_dir = 'static'
    for brick_path, basename in find_files(original_dir, ['*.css', '*.js', '*.tag']):
        static_path = brick_path.replace(original_dir, link_dir)
        if not os.path.exists(static_path):
            os.makedirs(static_path)
        # Make symlinks
        rel_path = os.path.relpath(original_dir, static_path)
        rel = os.path.join(brick_path.replace(original_dir, rel_path), basename)
        dst = os.path.join(static_path, basename)
        print(rel, dst)
        if not os.path.islink(dst):
            os.symlink(rel, dst)
    with fab_context.lcd(link_dir):
        # Remove all broken links
        local('find -xtype l -delete')


"""
[Service]
Type=oneshot
WorkingDirectory=/var/backup/%i
ExecStart=/bin/bash /var/backup/%i/backup.sh
SyslogIdentifier=backup
User=%i
"""

"""
[Unit]
Description=Daily backup

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""

"""
#!/bin/bash
/usr/pgsql-9.4/bin/pg_dumpall | /bin/gzip \
> /var/backup/postgres/$(date +"%d").sql.gz
"""

"""
#!/bin/bash
mysqldump -u backup --password= \
--all-databases --single-transaction --quote-names \
| /bin/gzip > /var/backup/mysql/$(date +"%d").sql.gz
"""
