
import pkg_resources
from pkg_resources import (
    working_set,
    DistributionNotFound,
    VersionConflict,
    UnknownExtra,
)

from docido_sdk.toolbox.text import exception_to_unicode


def _enable_plugin(env, module):
    """Enable the given plugin module if it wasn't disabled explicitly."""
    if env.is_component_enabled(module) is None:
        env.enable_component(module)


def load_eggs(entry_point_name):
    """Loader that loads any eggs in `sys.path`."""
    def _load_eggs(env):
        distributions, errors = working_set.find_plugins(
            pkg_resources.Environment()
        )
        for dist in distributions:
            if dist not in working_set:
                env.log.debug('Adding plugin %s from %s', dist, dist.location)
                working_set.add(dist)

        def _log_error(item, e):
            ue = exception_to_unicode(e)
            if isinstance(e, DistributionNotFound):
                env.log.debug('Skipping "%s": ("%s" not found)', item, ue)
            elif isinstance(e, VersionConflict):
                env.log.error('Skipping "%s": (version conflict "%s")',
                              item, ue)
            elif isinstance(e, UnknownExtra):
                env.log.error('Skipping "%s": (unknown extra "%s")', item, ue)
            else:
                env.log.error('Skipping "%s": %s', item,
                              exception_to_unicode(e, traceback=True))

        for dist, e in errors.iteritems():
            _log_error(dist, e)

        for entry in sorted(working_set.iter_entry_points(entry_point_name),
                            key=lambda entry: entry.name):
            env.log.debug(
                'Loading %s from %s',
                entry.name,
                entry.dist.location
            )
            try:
                entry.load(require=True)
            except Exception as exc:
                _log_error(entry, exc)
            else:
                _enable_plugin(env, entry.module_name)
    return _load_eggs


def load_components(env, loaders=(load_eggs('docido.plugins'),)):
    """Load all plugin components found in `sys.path`."""
    for loadfunc in loaders:
        loadfunc(env)
