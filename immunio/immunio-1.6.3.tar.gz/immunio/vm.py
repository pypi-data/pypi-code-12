import os
import sys
from pkg_resources import resource_filename

from immunio.deps import lupa


class VMError(Exception):
    """
    Raised for errors coming from within the Lua VM.
    """


class VM(object):
    def __init__(self, vm_globals=None):
        """
        NOTE: All values in vm_globals will be available to `boot.lua` but
              the values will only be available to hook code if they are
              also added to the SANDBOX_ENV in `boot.lua`.
        """
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)

        # Bootstrap the VM ...

        # Define load path for `require`.
        path = os.path.dirname(
            resource_filename(__name__, "lua-hooks/lib/boot.lua"))
        lexer_path = os.path.join(path, "lexers/")

        self.lua.execute('package.path = "%s/?.lua;%s/?.lua"' % (
            path, lexer_path))

        # Pass globals to boot.lua
        if vm_globals:
            for name, value in vm_globals.items():
                self.set_global(name, value)

        # Boot it. Yeaaaaah!
        self.lua.execute('require "boot"')

        # Save a reference Lua functions we'll call many times.
        self.sandboxed_call = self.lua.eval("sandboxed_call")
        self.load_lua = self.lua.eval(
            "function(...) return assert(loadstring(...)) end")

    def create_function(self, code, name=None):
        """
        Compile some Lua source.
        """
        try:
            func = self.load_lua(code, name)
            # If there is a compilation error, func will be a (None, err) tuple.
            # If compilation was successful, `func` will be a Lua code object.
            if isinstance(func, tuple):
                func, err = func
                if err is not None:
                    raise VMError(err)
            return func
        except lupa.LuaError, e:
            raise VMError, e, sys.exc_info()[2]

    def create_object(self, new_object):
        """
        Converts a Python container to Lua table.
        """
        if isinstance(new_object, dict):
            d = {}
            for key, value in new_object.iteritems():
                d[key] = self.create_object(value)
            new_object = d
        elif isinstance(new_object, (list, tuple,)):
            new_object = [self.create_object(value) for value in new_object]
        else:
            return new_object

        return self.lua.table_from(new_object)

    def to_python(self, table):
        """
        Converts a Lua object to Python.
        """
        if lupa.lua_type(table) != 'table':
            return table

        if table[1] is not None:
            # List
            object = [self.to_python(i) for i in table.values()]
        else:
            # Dict
            object = {}
            for key, value in table.items():
                object[key] = self.to_python(value)

        return object

    def call(self, func, vars=None):
        try:
            return self.sandboxed_call(func, self.create_object(vars))
        except lupa.LuaError, e:
            raise VMError, e, sys.exc_info()[2]

    def set_global(self, name, value):
        self.lua.globals()[name] = value

    def get_sandbox_global(self, name):
        return self.sandbox_env()[name]

    def set_serverdata(self, serverdata):
        self.sandbox_env()["serverdata"] = self.create_object(serverdata)

    def sandbox_env(self):
        return self.lua.globals()
