import os
from actors import create_actor, delete_actor
from slactorbot.plugins import import_plugin, plugins_dir
from utils import md5


def _new_plugin(actor_system, plugin_actors,plugin_name):
    plugin_import = import_plugin(plugin_name)
    plugin_md5 = md5(os.path.join(plugins_dir(), plugin_name + '.py'))
    plugin_actor = create_actor(actor_system, plugin_import.Main)
    plugin_actors[plugin_name] = {"actor": plugin_actor, "md5": plugin_md5}
    print "new plugin loaded: %s" % plugin_name
    return plugin_actors


def _change_plugin(actor_system, plugin_actors, plugin_name):
    print "changed plugin: %s" % plugin_name
    plugin_actors = _delete_plugin(actor_system, plugin_actors, plugin_name)
    plugin_actors = _new_plugin(actor_system, plugin_actors, plugin_name)
    return plugin_actors


def _delete_plugin(actor_system, plugin_actors, plugin_name):
    actor = plugin_actors[plugin_name]['actor']
    delete_actor(actor_system, actor)
    plugin_actors.pop(plugin_name, None)
    print "plugin deleted: %s" % plugin_name
    return plugin_actors


def load_plugins(actor_system, plugin_actors):
    plugin_files = os.listdir(plugins_dir())
    for _plugin in plugin_files:
        if _plugin.endswith('.py') and not _plugin.startswith('_'):
            plugin_name = _plugin[:-3]
            plugin_md5 = md5(os.path.join(plugins_dir(), _plugin))
            try:
                # if it's a new plugin not seen before create an actor
                if plugin_name not in plugin_actors.keys():
                    plugin_actors = _new_plugin(actor_system, plugin_actors, plugin_name)

                # if it's a modified plugin delete the old actor and create a new one
                if plugin_md5 != plugin_actors[plugin_name]['md5']:
                    plugin_actors = _change_plugin(actor_system, plugin_actors, plugin_name)

            except AttributeError:
                continue

    # if the plugin no longer exists on disk remove it
    for cached_plugin in plugin_actors.keys():
        if cached_plugin + '.py' not in plugin_files:
            plugin_actors = _delete_plugin(actor_system, plugin_actors, cached_plugin)

    return plugin_actors

