from __future__ import print_function

# Adapted from http://code.activestate.com/recipes/577058/
def confirm(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True or False.
    """
    import sys

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def create_conditional_print(should_print):
    '''
    When should_print is True, returns a function which prints its inputs.
    When it's false, return a function which does nothing.

    Usage:

    def do_something(verbose=False):
        from bodylabs.util.console import create_conditional_print
        print_verbose = create_conditional_print(verbose)

        print_verbose('Here is something which might print')

    '''
    def noop(*args, **kwargs): # Yup, these args are unused in this no-op function... pylint: disable=unused-argument
        pass

    if should_print:
        return print
    else:
        return noop

def sizeof_format_human_readable(num):
    '''
    Sweet little implementation from
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    '''
    for x in ['b', 'kb', 'mb', 'gb']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'tb')
