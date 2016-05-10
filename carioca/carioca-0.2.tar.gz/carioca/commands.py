#
# The MIT License (MIT)
#
# Copyright (c) 2016 eGauge Systems LLC
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import re
import textwrap

class Error(Exception):
    pass

class Command_Done(Exception):
    pass

functions = {
    'mac_addr':	True,
    'int':	True,
}

quoted_string_pat = r'"((\\.|[^\\"])*)"'
varname_pat = r'[a-z_][a-z_0-9]*'
non_blank_pat = r'[^ \t]+'


def get_var(scope, varname):
    if varname not in scope:
        raise Error('Unknown variable name `%s\'' % varname)
    return scope[varname]

def get_int(arg):
    try:
        return int(arg, 0)
    except ValueError:
        raise Error('Value `%s\' is not a valid integer literal' % arg)

def get_string(arg):
    return re.sub(r'\\(.)', r'\1', arg)

def func_int(scope, args_string):
    """Expects a single string argument.  The function converts the string
    argument to a number and returns that number as its value.  A prefix
    of 0x can be used to specify a hex number; a prefix of 0o can be
    used to specify an octal number.

    """
    m = re.match(varname_pat, args_string, flags=re.IGNORECASE)
    if m:
        val = get_var(scope, args_string)
    else:
        m = re.match(quoted_string_pat + '$', args_string, flags=re.IGNORECASE)
        if not m:
            raise Error('Argument `%s\' is not a variable name or string'
                        % val)
        val = get_string(m.group(1))
    return get_int(val)

def func_mac_addr(scope, args_string):
    """Expects a single string argument specifying a MAC address in the
    form aa:bb:cc:dd:ee:ff, that is, six hex numbers separated by
    colons.  The function converts each hex string to a byte and
    returns them as a list of six bytes.

    """
    m = re.match(varname_pat, args_string, flags=re.IGNORECASE)
    if m:
        val = get_var(scope, args_string)
    else:
        m = re.match(quoted_string_pat + '$', args_string, flags=re.IGNORECASE)
        if not m:
            raise Error('Argument `%s\' is not a variable name or string'
                        % val)
        val = get_string(m.group(1))
    m = re.match(r'([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2})'
                 ':([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2})',
                 val, re.IGNORECASE)
    if not m:
        raise Error('Argument `%s\' is not a MAC address of '
                    'the form aa:bb:cc:dd:ee:ff' % val)
    return [ int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16),
             int(m.group(4), 16), int(m.group(5), 16), int(m.group(6), 16) ]

def fun_call(scope, name, args_string):
    if name not in functions:
        raise Error('Unknown function name `%s\'' % name)
    func = globals()['func_' + name]
    return func(scope, args_string)

def parse_value(scope, arg):
    m = re.match(r'([a-z_][a-z_0-9]*)[(]([^)]*)[)]', arg, flags=re.IGNORECASE)
    if m:
        # function call
        return fun_call(scope, name=m.group(1), args_string=m.group(2))

    m = re.match(varname_pat, arg, flags=re.IGNORECASE)
    if m:
        return get_var(scope, arg)
    m = re.match(quoted_string_pat + r'$', arg, flags=re.IGNORECASE)
    if m:
        # string literal
        return get_string(m.group(1))
    return get_int(arg)

def parse_value_list(scope, arg):
    str_list = arg.split(',')
    ret = []
    for str in str_list:
        val = parse_value(scope, str.strip())
        if type(val) is list:
            ret += val
        else:
            ret.append(val)
    return ret

def parse_string(scope, arg):
    val = parse_value(scope, arg)
    if type(val) is not str:
        raise Error('Invalid string `%s\'' % arg)
    return val

def parse_number(scope, arg):
    val = parse_value(scope, arg)
    if type(val) is not int:
        raise Error('Invalid number `%s\'' % arg)
    return val

def parse_address(scope, arg):
    return parse_number(scope, arg)

def parse_number_list(scope, arg):
    l = parse_value_list(scope, arg)
    for val in l:
        if type(val) is not int:
            raise Error('Invalid number list `%s\'' % arg)
    return l

def parse_variable(scope, arg):
    if not re.match(r'[a-z_][a-z_0-9]*', arg, flags=re.IGNORECASE):
        raise Error('Illegal variable name `%s\'' % arg)
    return arg

cmd_list = {
    'go':	[ True, parse_address ],
    'help':	[ False ],
    'print':	[ False, parse_string, parse_value_list ],
    'quit':	[ False ],
    'readb':	[ True,  parse_variable, parse_address, parse_number ],
    'readh':	[ True,  parse_variable, parse_address, parse_number ],
    'readw':	[ True,  parse_variable, parse_address, parse_number ],
    'reads':	[ True,  parse_variable, parse_address, parse_number ],
    'readimg':	[ True,  parse_address, parse_number, parse_string ],
    'sendimg':	[ True,  parse_address, parse_string ],
    'set':	[ False, parse_variable, parse_value ],
    'default':	[ False, parse_variable, parse_value ],
    'writeb':	[ True,  parse_address, parse_number_list ],
    'writeh':	[ True,  parse_address, parse_number_list ],
    'writew':	[ True,  parse_address, parse_number_list ],
    'writes':	[ True,  parse_address, parse_string ],
}

def cmd_go(scope, samba, args):
    """Jump to specified ADDRESS and switch to terminal-emulation mode."""
    samba.go(addr=args[0])
    raise Command_Done('go')

def cmd_writes(scope, samba, args):
    """Write STRING to ADDRESS.  A trailing 0 byte will stored after the
    end of the string.

    """
    addr = args[0]
    blist = bytes(args[1], 'utf-8')
    for byte in blist:
        samba.write_byte(addr, int(byte))
        addr += 1
    samba.write_byte(addr, 0)

def cmd_writeb(scope, samba, args):
    """Write the bytes in the NUMBER_LIST to memory starting at ADDRESS.

    """
    addr = args[0]
    for val in args[1]:
        samba.write_byte(addr, val)
        addr += 1

def cmd_writeh(scope, samba, args):
    addr = args[0]
    for val in args[1]:
        samba.write_halfword(addr, val)
        addr += 2

def cmd_writew(scope, samba, args):
    addr = args[0]
    for val in args[1]:
        samba.write_word(addr, val)
        addr += 4

def cmd_reads(scope, samba, args):
    varname = args[0]
    addr = args[1]
    count = args[2]
    ret = ''
    for i in range(count):
        val = samba.read_byte(addr)
        if val == 0:
            break
        ret += chr(val)
        addr += 1
    scope[varname] = ret

def cmd_readb(scope, samba, args):
    """Read NUMBER bytes starting at ADDRESS and store the result in
    VARIABLE.  If NUMBER is equal to 1, the read value is stored
    directly in VARIABLE.  If NUMBER is greater than 1, the read
    values are stored as a list of values of length NUMBER.

    """
    varname = args[0]
    addr = args[1]
    count = args[2]
    if count < 1:
        return
    l = []
    for i in range(count):
        val = samba.read_byte(addr)
        l.append (val)
        addr += 1
    scope[varname] = l if len(l) > 1 else l[0]

def cmd_readh(scope, samba, args):
    """Read NUMBER halfwords starting at ADDRESS and store the result in
    VARIABLE.  If NUMBER is equal to 1, the read value is stored
    directly in VARIABLE.  If NUMBER is greater than 1, the read
    values are stored as a list of values of length NUMBER.

    """
    varname = args[0]
    addr = args[1]
    count = args[2]
    if count < 1:
        return
    l = []
    for i in range(count):
        val = samba.read_halfword(addr)
        l.append (val)
        addr += 2
    scope[varname] = l if len(l) > 1 else l[0]

def cmd_readw(scope, samba, args):
    """Read NUMBER words starting at ADDRESS and store the result in
    VARIABLE.  If NUMBER is equal to 1, the read value is stored
    directly in VARIABLE.  If NUMBER is greater than 1, the read
    values are stored as a list of values of length NUMBER.

    """
    varname = args[0]
    addr = args[1]
    count = args[2]
    if count < 1:
        return
    l = []
    for i in range(count):
        val = samba.read_word(addr)
        l.append (val)
        addr += 4
    scope[varname] = l if len(l) > 1 else l[0]

def cmd_sendimg(scope, samba, args):
    """Send the binary image with filename STRING to memory starting at
    ADDRESS.

    """
    addr = args[0]
    filename = args[1]
    try:
        stream = open(filename, 'rb')
    except:
        raise Error('Failed to open file `%s\' for reading: %s' %
                    filename, sys_exc_info()[1])
    samba.send_file(addr, stream)

def cmd_readimg(scope, samba, args):
    """Read NUMBER of bytes from memory starting at ADDRESS and store them
    as a binary image in a file with name STRING.

    """
    addr = args[0]
    count = args[1]
    filename = args[2]
    try:
        stream = open(filename, 'wb')
    except:
        raise Error('Failed to open file `%s\' for writing: %s' %
                    filename, sys_exc_info()[1])
    samba.receive_file(addr, count, stream)

def cmd_print(scope, samba, args):
    """Output the values in VALUE_LIST according to the format given by
    STRING.  The values are formatted using the Python format()
    function so any of its supported format specifiers can be used.
    Most simply, the values can be referred by position.  For example:
    ``print "the answer is {0} not {1}" 42, 43'' would print "the
    answer is 42 not 43" since 42 and 43 are the first and second
    positional argument, respectively.  If the arguments values are
    printed in order, you can omit the argument number.  For example
    ``print "{} {}" 42, 43'' would also print "42 43".  Formatting
    characters can be specified after a colon.  For example, ``print
    "0x{:04x}" 42'' would print "0x002a".

    """
    fmt = args[0]
    print(fmt.format(*args[1]))

def cmd_set(scope, samba, args):
    """Set VARIABLE to VALUE.

    """
    varname = args[0]
    val = args[1]
    scope[varname] = val

def cmd_default(scope, samba, args):
    """Sets VARIABLE to VALUE but only if VARIABLE isn't defined already.

    """
    varname = args[0]
    val = args[1]
    if varname in scope:
        return
    scope[varname] = val

def cmd_help(scope, samba, args):
    """Print this help message."""
    wrapper = textwrap.TextWrapper(initial_indent='\t',
                                   subsequent_indent='\t')
    intro = ('Line-comments start with the hash characer (#).\n'
             'Lines ending with a backslash (\\) are merged with the '
             'next line, replacing any white space at the start of the '
             'next line with a single blank.\n'
             'NUMBER is an integer number.  A prefix of 0x can be used to '
             'to indicate a hexadecimal number or a prefix of 0o can be used '
             'to indicate an octal number.\n'
             'ADDRESS is a number that is interpreted as a memory address.\n'
             'STRING is a string of characters that must be enclosed '
             'in double quotes. '
             'Special characters such as double quote or backslash can '
             'be included in a string by escaping them with a backslash (\\) '
             'character.\n'
             'VALUE may be a STRING or NUMBER.\n'
             'NUMBER_LIST represents a list of comma-separated NUMBERs.\n'
             'VALUE_LIST represents a list of comma-separated numbers or '
             'strings.\n'
             'A variable name can be specified where a literal value '
             'is expected, provided the variable contains a value '
             'of the required type.\n'
             'A function call may also be used in place of a literal value. '
             'The following functions are available:')
    for paragraph in intro.split('\n'):
        for line in textwrap.wrap(paragraph, initial_indent='\n'):
            print(line)

    for name in sorted(functions.keys()):
        func = globals()['func_' + name]
        print('\n %s()' % name)
        if func.__doc__ is not None:
            for line in wrapper.wrap(func.__doc__):
                print(line)

    print('\nAvailable commands:')

    for cmd in sorted(cmd_list.keys()):
        func = globals()['cmd_' + cmd]
        args = []
        for parser in cmd_list[cmd][1:]:
            arg_type = parser.__name__.upper()
            m = re.match(r'parse_(.*)', arg_type, flags=re.IGNORECASE)
            if m:
                arg_type = m.group(1)
            args.append(arg_type)
        print('\n  %s %s' % (cmd, ' '.join(args)))
        if func.__doc__ is not None:
            for line in wrapper.wrap(func.__doc__):
                print(line)

def cmd_quit(scope, samba, args):
    """Exit carioca."""
    raise Command_Done('quit')

def execute(scope, get_samba, line):
    res = line.split(maxsplit=1)
    cmd = res[0]
    rest = res[1] if len(res) > 1 else ''
    if cmd not in cmd_list:
        raise Error('Unknown command `%s\'' % cmd)
    cmd_spec = cmd_list[cmd]
    samba = get_samba() if cmd_spec[0] else None
    pat = r'(' + quoted_string_pat + r')|' + non_blank_pat
    arg_string = []
    for m in re.finditer(pat, rest, flags=re.IGNORECASE):
        if len(arg_string) >= len(cmd_spec) - 1:
            arg_string[len(arg_string) - 1] += ' ' + m.group(0)
        else:
            arg_string.append(m.group(0))
    if len(arg_string) != len(cmd_spec) - 1:
        raise Error('Command `%s\' requires %u argument(s) but %u given' %
                    (cmd, len(cmd_spec) - 1, len(arg_string)))
    args = []
    for i in range(len(arg_string)):
        args.append(cmd_spec[i + 1](scope, arg_string[i]))
    func = globals()['cmd_' + cmd]
    func(scope, samba, args)
