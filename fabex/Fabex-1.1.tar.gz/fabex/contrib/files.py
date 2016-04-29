from __future__ import unicode_literals

from os.path import isabs, join
from fabric.api import env
from fabric.contrib.files import *
from fabric.contrib.files import (exists as fab_exists,
                                  upload_template as fab_upload_template,
                                  sed as fab_sed,
                                  append as fab_append,
                                  )

from fabric.operations import _AttributeList # to mimic in dryruns
from jinja2 import Environment
from ..fab_api import print_command, sudo, run
from ..exceptions import FabexConfigError, FabexRunError

__all__ = ['exists', 'upload_template', 'sed', 'append', 'upload_project_template',
           'rm_project_template']

def exists(path, **kwargs):
    __doc__ = fab_exists.__doc__

    if env.dryrun:
        return False
    return fab_exists(path, **kwargs)


def upload_template(filename, destination, **kwargs):
    __doc__ = fab_exists.__doc__

    if env.dryrun:
        print_command("upload_template {} -> {}".format(filename, destination))

        return _AttributeList(destination)
    return fab_upload_template(filename, destination, **kwargs)


def sed(filename, before, after, **kwargs):
    __doc__ = fab_sed.__doc__
    if env.dryrun:
        args = {'backup': kwargs.get('backup', '.bak'),
                'limit': kwargs.get('limit', ''),
                'flags': kwargs.get('flags', ''),
                'before': before,
                'after': after,
                'filename': filename,
               }
        print_command('sed -i{backup} -r -e "/{limit}/ '
                      's/{before}/{after}/{flags}g {filename}"'
                      .format(**args))
        return "[sed output]"
    return fab_sed(filename, before, after, **kwargs)


def append(filename, text, **kwargs):
    __doc__ = fab_append.__doc__
    if env.dryrun:
        print_command("append {}->{}".format(filename, text))
        return
    return fab_append(filename, text, **kwargs)



def jinja2_string(template, context=env):
    return Environment().from_string(template).render(**context)


def get_templates(templates=[]):
    """Returns each of the templates with env vars injected."""
    injected = {}
    for name, data in (t for t in env.fabex_templates.iteritems()
                       if not templates or t[0] in templates):
        injected[name] = {k: jinja2_string(v) for k, v in data.items()}
    return injected


def upload_project_template(name, force=False, reload=True):
    """Uploads a template if changed. Execute reload_command if changed and reload. """
    try:
        template = get_templates([name])[name]
    except KeyError:
        raise FabexConfigError("missing template: {}".format(name))
    local_path = template["local_path"]
    if not isabs(local_path):
        local_path = join(env.fabex_config['template_dir'], local_path)
    if not os.path.exists(local_path):
        raise FabexRunError("template {} not found at {}".format(name, local_path))
    remote_path = template["remote_path"]
    reload_command = template.get("reload_command")
    owner = template.get("owner")
    mode = template.get("mode")
    remote_data = ""
    if exists(remote_path):
        with hide("stdout"):
            remote_data = sudo("cat %s" % remote_path, quiet=True, shell=False)
    with open(local_path, "r") as f:
        local_data = jinja2_string(f.read())
    whitewash = lambda s: re.sub(r"(?m)\s+", "", s)
    if whitewash(remote_data) == whitewash(local_data):
        if force:
            print_command("Template {} unchanged, but force=True".format(name), arrow_out=False)
        else:
            print_command("Template {} unchanged, not uploading".format(name), arrow_out=False)
            return
    upload_template(local_path, remote_path, context=env,
                    use_sudo=True, backup=False, use_jinja=True)
    if owner:
        sudo("chown %s %s" % (owner, remote_path))
    if mode:
        sudo("chmod %s %s" % (mode, remote_path))
    if reload and reload_command:
        return sudo(reload_command)
    return ""


def rm_project_template(name, reload=True, force=False):
    """Removes a template on the remote host"""
    try:
        template = get_templates([name])[name]
    except KeyError:
        raise FabexConfigError("missing template: {}".format(name))
    remote_path = template["remote_path"]
    reload_command = template.get("reload_command")
    if not exists(remote_path):
        if force:
            return ""
        raise FabexRunError("template {} does not exist at remote path {}"
                            .format(name, remote_path))
    sudo("rm -v -f " + remote_path)
    if reload and reload_command:
        return sudo(reload_command)
    return ""


