import sys
import importlib
import traceback

import lupa
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
sys.modules['prosodypy'].lua = lua
execute_lua_file = sys.modules['prosodypy'].execute_lua_file

def load_code_factory(orig_load_code):
    install_pymodule_paths()
    def load_code(plugin, resource, env):
        if plugin.startswith('!py:'):
            try:
                plugin = importlib.import_module(plugin[4:]).ProsodyPlugin(env, lua)
            except Exception as e:
                return False, traceback.format_exc()
            return plugin, ""
        else:
            return orig_load_code(plugin, resource, env)
    return load_code

def install_pymodule_paths():
    config = lua.require("core.configmanager")
    paths = config.get("*", "plugin_paths")
    for i in paths:
        sys.path.insert(0, paths[i])

lua_globs = lua.globals()
lua_globs.arg = lua.table_from(sys.argv[1:])
lua_globs.load_code_factory = load_code_factory

orig_lua_select = lua_globs.select
lua.eval('''
function(load_code_factory, orig_lua_select)
    local swapped = false;
    _G.select = function(...)
        if not swapped then
            swapped = true;
            local pluginloader = require "util.pluginloader";
            pluginloader.load_code = load_code_factory(pluginloader.load_code);
            _G.select = orig_lua_select;
        end
        return _G.select(...);
    end
end
''')(load_code_factory, orig_lua_select)

execute_lua_file(lua, '/usr/bin/prosody') # TODO: don't hardcode
