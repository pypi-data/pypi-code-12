from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from immunio.logger import log
from immunio.timer import Timer
import immunio.plugins.plugin_django
import immunio.plugins.plugin_django_xss
import immunio.plugins.plugin_fileio
import immunio.plugins.plugin_flask
import immunio.plugins.plugin_jinja2
import immunio.plugins.plugin_mysqldb
import immunio.plugins.plugin_psycopg2
import immunio.plugins.plugin_pyramid
import immunio.plugins.plugin_pysqlite2
import immunio.plugins.plugin_shell
import immunio.plugins.plugin_sqlite3


# Plugins listed here will be enabled by default. The final list can be
# adjusted by settings the `plugins_enabled` and `plugins_disabled` config
# settings.
DEFAULT_PLUGINS = [
    # Core python
    "file_io",
    "shell",
    # Libraries
    "sqli_sqlite",
    "sqli_psycopg2",
    "sqli_mysqldb",
    "xss_jinja2",
    # "xss_django", - disabled by default for first release.
    # Main Frameworks
    "django",
    "flask",
    "pyramid",
]


def build_active_plugins(config):
    """
    Build and return a `set()` of currently active plugin names based
    on the defaults above and any `plugins_enabled` or `plugins_disabled`
    values in the supplied config.
    """
    # start with the defaults enabled
    active = set(DEFAULT_PLUGINS)

    # Add any specifically enabled
    manually_enabled = config.get("plugins_enabled", set(), set)
    active |= manually_enabled

    # And finally remove any specifically disabled. This ensures disabled
    # has priority over enabled.
    manually_disabled = config.get("plugins_disabled", set(), set)
    active -= manually_disabled

    return active


class PluginManager(object):
    """
    Manages all plugins.
    """
    def __init__(self, config, get_agent_func=None):
        self._hook_callback = None
        self._timer = Timer()
        self.get_agent_func = get_agent_func

        # Build a set of currently enabled plugins
        self.active_plugins = build_active_plugins(config)
        log.info("Active Plugins: %s", self.active_plugins)

        self.patch()

    def set_hook_callback(self, hook_callback):
        """
        Set the hook callback function to receive hook events from
        monkey-patched modules.

        It should only ever be set once so raise an Exception if it's
        already set.
        """
        if self._hook_callback:
            raise Exception("PluginManager hook_callback is already set")
        self._hook_callback = hook_callback

    def set_timer_callback(self, timer_callback):
        """
        Set the `Timer` instance to be used to measure plugin durations. If
        no timer is set, the plugin durations will not be timed.
        """
        self._timer.set_report_callback(timer_callback)

    def patch(self):
        """
        Actually run all the plugins to monkeypatch the code.
        """
        # The order here is significant.
        # Patch low-level calls first
        self.register(immunio.plugins.plugin_fileio)
        self.register(immunio.plugins.plugin_shell)
        # Patch database drivers next since they are used by frameworks.
        self.register(immunio.plugins.plugin_sqlite3)
        self.register(immunio.plugins.plugin_pysqlite2)
        self.register(immunio.plugins.plugin_mysqldb)
        self.register(immunio.plugins.plugin_psycopg2)
        # Patch support libraries used by frameworks
        self.register(immunio.plugins.plugin_jinja2)
        self.register(immunio.plugins.plugin_django_xss)
        # Patch web frameworks next.
        self.register(immunio.plugins.plugin_django)
        self.register(immunio.plugins.plugin_flask)
        self.register(immunio.plugins.plugin_pyramid)

    def register(self, plugin_module):
        """
        Call the module to do the monkeypatching and give it a `run_hook`
        function to be used by the patched methods.
        """
        plugin_module_name = plugin_module.__name__

        # Only add plugins that are currently enabled.
        if plugin_module.NAME not in self.active_plugins:
            return

        def run_hook(hook, meta):
            """
            Closure to add the name to the run_hook call.
            """
            return self._run_hook(plugin_module_name, hook, meta)

        # Actually do the monkeypatching
        plugin_module.add_hooks(run_hook, get_agent_func=self.get_agent_func,
                                timer=self._timer)

    def _run_hook(self, plugin_name, hook, meta):
        """
        Receives all hook calls from the monkeypatched code. If a callback
        is set, pass the data through.

        This function also enforces the guarantee that the `run_hook` function
        passed to plugins will always return a dict.
        """
        if not self._hook_callback:
            return {}

        result = self._hook_callback(plugin_name, hook, meta)
        if not isinstance(result, dict):
            log.warn("Code for hook `%(hook)s` returned non-dict result.", {
                "hook": hook,
            })
            return {}
        return result
