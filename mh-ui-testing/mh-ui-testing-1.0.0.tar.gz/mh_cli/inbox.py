import click
from mh_cli import cli

from common import inbox_options, init_fabric, pass_state
from click.exceptions import UsageError
from fabric.context_managers import cd
from os.path import basename, exists, getsize
from fabric.api import run, abort, hide, sudo
from fabric.operations import put
from fabric.colors import cyan
from fabric.contrib.files import exists as remote_exists


@cli.group()
def inbox():
    """Manipulate the MH recording file inbox"""


@inbox.command(name='put')
@click.option('-f', '--file')
@inbox_options
@pass_state
@init_fabric
def inbox_put(state, file):
    """Upload a recording file to the MH inbox"""
    if file.startswith('http'):
        with cd(state.inbox_path):
            sudo("curl -s -o %s %s" % (basename(file), file))
        result = state.inbox_path + '/' + basename(file)
    elif exists(file):
        size_in_bytes = getsize(file)
        if size_in_bytes / (1024 * 1024) > 1024:
            raise UsageError(
                "File > 1G. Upload to s3 and use the url instead.")
        result = put(local_path=file,
                     remote_path=state.inbox_path, use_sudo=True)
    else:
        raise UsageError("Local file %s not found" % file)
    print(cyan("Files created: {}".format(str(result))))


@inbox.command(name='symlink')
@click.option('-f', '--file')
@click.option('-c', '--count', type=int, default=1)
@inbox_options
@pass_state
@init_fabric
def inbox_symlink(state, file, count):
    """Create copies of an existing inbox file via symlinks"""
    remote_path = state.inbox_dest.child(file)
    if not remote_exists(remote_path, verbose=True):
        abort("remote file {} not found".format(remote_path))

    with cd(state.inbox_path):
        for i in range(count):
            link = remote_path.stem + '_' + str(i + 1) + remote_path.ext
            sudo("ln -sf {} {}".format(remote_path, link))
        return


@inbox.command(name='list')
@click.argument('match', default='')
@inbox_options
@pass_state
@init_fabric
def inbox_list(state, match):
    """List the current contents of the inbox"""
    if not remote_exists(state.inbox_dest):
        return
    with cd(state.inbox_dest), hide('running', 'stdout', 'stderr'):
        output = run('ls {} | grep -v "\.md5"'.format(match),
                     warn_only=True, quiet=True)
        for f in output.split():
            print(cyan(f))
