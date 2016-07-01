# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Bootstrap the agent instance.

"""

import hashlib
import imp
import logging
import os
import platform
import shutil
import sys

from appdynamics import get_build_filename, get_version


def get_ucs():
    ucs = 'ucs4' if sys.maxunicode > 65535 else 'ucs2'
    return ucs


# Les fossoyeurs de l'esperance affutent leurs longs couteaux.
def make_virtual_bindeps_package():
    """Workaround for lack of Python 2.x ABI.

    The embedded zmq libraries are specific to cp27m, cp27mu, etc. builds
    because they look for the UTF8/UTF16 string versions. Unfortunately, we
    have no way of specifying the Python ABI as part of the dependencies, so
    we can't take the correct precompiled version.

    Instead, we have bindeps ship the wide and narrow Unicode versions, and
    then construct a "virtual" bindeps package by symlinking the right
    version. We have to do this instead of just aliasing the import because
    there's otherwise no way to deal with the "appdynamics_bindes.zmq"
    imports inside the zmq code.

    """

    from appdynamics import config

    # Get the location of the actual package in the current Python env.
    import appdynamics_bindeps
    src_root = os.path.dirname(appdynamics_bindeps.__file__)
    del sys.modules['appdynamics_bindeps']

    pyver = '.'.join(platform.python_version_tuple()[:2])
    ucs = get_ucs()
    src_hash = hashlib.md5(src_root).hexdigest()

    # Here's where things start to get freaky. We need to avoid sharing our
    # virtual package because it might point to a virtualenv that has since
    # been destroyed, obliterating our links. We also need to avoid sharing
    # virtual packages for different versions of the agent. This accomplishes
    # both by using the actual location of the real package as part of the
    # name of the location of our virtual package.
    prefix = "python%s-%s-%s" % (pyver, ucs, src_hash)

    dest_root = os.path.join(config.DIR, 'lib', prefix, 'site-packages')
    dest = os.path.join(dest_root, 'appdynamics_bindeps')
    tombstone = os.path.join(dest, 'TOMBSTONE')

    tombstone_version = get_version(tombstone, noisy=False)
    build_version = get_version(noisy=False)

    if tombstone_version == 'unknown' or tombstone_version != build_version:
        # This gets really weird because we could be racing other processes
        # trying to build the virtual package. Even if we know we are losing
        # the race, it's better to keep racing to ensure that at the end, the
        # virtual package is completely built.
        try:
            try:
                os.makedirs(dest)
            except:
                if not os.path.exists(dest):
                    raise
                pass  # Someone else beat us to the punch.

            zmq_target = 'zmq_' + ucs

            for fn in os.listdir(src_root):
                src = os.path.join(src_root, fn)

                if fn == zmq_target:
                    link_dest = os.path.join(dest, 'zmq')
                elif not fn.startswith('zmq'):
                    link_dest = os.path.join(dest, fn)
                else:
                    continue

                try:
                    os.symlink(src, link_dest)
                except:
                    if not os.path.exists(link_dest):
                        raise
                    pass  # Someone else beat us to the punch.

            try:
                # Mark the virtual package as being completely built.
                shutil.copyfile(get_build_filename(), tombstone)
            except:
                pass
        except:
            logging.exception('AppDynamics Python agent startup failed making virtual package')
            pass

    sys.path.insert(0, dest_root)


def import_zmq():
    try:
        __import__('appdynamics_bindeps.zmq')
    except ImportError:
        make_virtual_bindeps_package()


import_zmq()


from appdynamics import config
from appdynamics.agent.core.logs import configure_logging
from appdynamics.agent.core.agent import Agent
from appdynamics.agent.interceptor import BT_INTERCEPTORS, add_hook

_agent = None


def configure(environ=None):
    agent_config = config.parse_environ()
    if environ:
        agent_config.update(config.parse_environ(environ))

    config.merge(agent_config)
    configure_logging()

    return config.validate_config(agent_config)


def bootstrap(agent=None):
    try:
        global _agent

        _agent = agent or Agent()
        hook = add_hook(_agent)

        for mod, patch in BT_INTERCEPTORS:
            hook.call_on_import(mod, patch)

        _agent.module_interceptor = hook
        return _agent
    except:
        logging.getLogger('appdynamics.agent').exception('Error bootstrapping AppDynamics agent; disabling.')
        return None


def get_agent_instance():
    if _agent is None:
        return bootstrap()
    else:
        return _agent


def remove_autoinject():
    # Remove our injected sitecustomize and load the real one (if any).
    # We let this throw an ImportError because `site` already silences it.
    sys.modules.pop('sitecustomize', None)
    mod_data = imp.find_module('sitecustomize')
    mod = imp.load_module('sitecustomize', *mod_data)
    sys.modules.update(sitecustomize=mod)
