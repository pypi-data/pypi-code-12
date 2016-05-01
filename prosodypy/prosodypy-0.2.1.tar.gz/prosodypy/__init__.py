lua = None

def execute_lua_file(lua, filename):
    with open(filename, 'rb') as lua_file:
        code = lua_file.read()
    if code.startswith('#!'):
        code = code[code.find('\n'):]
    lua.execute(code)

