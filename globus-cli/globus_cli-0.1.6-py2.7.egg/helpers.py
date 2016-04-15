from __future__ import print_function
import sys
import json
import textwrap
import re


# Format Enum for output formatting
# could use a namedtuple, but that's overkill
JSON_FORMAT = 'json'
TEXT_FORMAT = 'text'

# what qualifies as a valid Identity Name?
_IDENTITY_NAME_REGEX = '^[a-zA-Z0-9]+.*@[a-zA-z0-9-]+\..*[a-zA-Z]+$'


def stderr_prompt(prompt):
    """
    Prompt for input on stderr.
    Good for not muddying redirected output while prompting the user.
    """
    print(prompt, file=sys.stderr, end='')
    return raw_input()


def outformat_is_json(args):
    return args.outformat == JSON_FORMAT


def outformat_is_text(args):
    return args.outformat == TEXT_FORMAT


def cliargs(helptext, *arguments, **kwargs):
    """
    Decorator that takes a function and adds CLI arguments and helptext to it
    as function attributes. The function can then be placed directly into the
    command hierarchy of the _COMMAND_TREE and will be unpacked and inspected
    by parser building.
    """
    def inner_decorator(wrapped):
        """
        The decorator produced by invoking cliargs() on some arguments.
        Doesn't need to create a closure over the wrapped function or anything:
        just takes the arguments to cliargs() and puts them into attributes of
        the function.
        """
        wrapped.cli_help = helptext
        wrapped.cli_arguments = arguments
        wrapped.cli_argument_validator = kwargs.get('arg_validator', None)

        return wrapped

    return inner_decorator


class CLIArg(object):
    def __init__(self, name, **kwargs):
        self.kwargs = kwargs
        self.name = name

        self.kwargs['dest'] = self.name.replace('-', '_')
        if 'help' in self.kwargs:
            self.kwargs['help'] = wrap_helptext(self.kwargs['help'])

    def argparse_arglist(self):
        return ['--{}'.format(self.name)]

    def argparse_kwargs(self):
        return self.kwargs

    def is_required(self):
        return 'required' in self.kwargs and self.kwargs['required']


def print_json_response(res):
    print(json.dumps(res.data, indent=2))


def colon_formatted_print(data, named_fields):
    maxlen = max(len(n) for n, f in named_fields) + 1
    for name, field in named_fields:
        print('{} {}'.format((name + ':').ljust(maxlen), data[field]))


def wrap_helptext(helptext, wraplen=50):
    # split the helptext into lines, wrap the lines, and join them back
    # together. This extra work is needed because textwrap's
    # replace_whitespace=False
    # option doesn't do what you think it does, and causes funny newlines in
    # the middle of output if left to its own devices
    lines = [textwrap.fill(line, width=wraplen, replace_whitespace=False)
             for line in helptext.splitlines()]
    return '\n'.join(lines)


def is_valid_identity_name(identity_name):
    """
    Check if a string is a valid identity name.
    Does not do any preprocessing of the identity name, so you must do so
    before invocation.
    """
    if re.match(_IDENTITY_NAME_REGEX, identity_name) is None:
        return False
    else:
        return True
