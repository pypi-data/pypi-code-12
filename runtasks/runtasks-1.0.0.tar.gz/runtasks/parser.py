
import sys, inspect, logging
from collections import OrderedDict

logger = logging.getLogger('')


def parse(args, tasks):
    """
    Parses command line arguments into groups of tasks and arguments to those tasks.

    Returns a sequence of (Task, args) pairs where the arguments are an inspect.BoundArguments
    instance.
    """
    results = []

    other_names = list(tasks.keys())

    while args:
        task = tasks.get(args[0])
        if not task:
            sys.exit("I don't know what %r is" % args[0])
        boundargs, args = parse_task(task, args, other_names)

        results.append( (task, boundargs) )

    return results


def parse_task(task, cmdline, other_names):
    """
    Parses the arguments for a single task.  Raises an exception if all required arguments are
    not provided.

    Since the command line may contain multiple tasks, it stops when all parameters have been
    assigned or when unrecognized tokens are found.

    cmdline:
      An array of strings, originally from sys.argv.  The name of this task will be the first
      item.

    other_names
      Names of other defined tasks.

    Returns the tasks arguments as an inspect.BoundArguments instance and the remaining,
    unparsed arguments: (BoundArguments, remaning-cmdline)
    """
    names  = list(task.sig.parameters.keys())
    params = list(task.sig.parameters.values())

    # How many positional parameters are required?  If there are unrecognized tokens we'll
    # assume they are values for these.  For example:
    #
    #   @task test(arg1, arg2=None)
    #
    #   build test xyz --> arg1=xyz
    #
    # We only read positional parameters like this until we hit the first parameter with
    # equals or dashes ("--arg1" or "arg1=xyz", etc.).  Once we hit one of those, we'll set
    # `positional` to None to indicate so.

    positional = []
    for param in params:
        if param.default == inspect.Parameter.empty:
            positional.append(param.name)
        else:
            break

    params = OrderedDict()
    # We'll copy values from the command line (tokens) to here by parameter name.

    cmdline = cmdline[1:] # we've now copied it

    while cmdline:
        arg = cmdline[0]

        if arg.startswith('--'):
            positional = None # Now that we've seen a named item, no more positional.
            _parse_double_dash(task, cmdline, params)

        elif arg.startswith('-'):
            positional = None
            _parse_flags(task, cmdline, params)

        elif '=' in arg:
            positional = None # Now that we've seen a named item, no more positional.
            _parse_equals(task, cmdline, params)

        elif positional:
            # This might be a value for the next positional item.  If it also matches a
            # task name, abort though.  We are not going to guess.
            if arg in other_names:
                sys.exit('%r can be a task or a positional argument.  Use dashes or equals to disambiguate' % arg)

            params[positional[0]] = cmdline.pop(0)
            positional.pop(0)

        else:
            break


    # Now make sure all of the required arguments have a default value.  Fortunately
    # Signature.bind will do this, raising a TypeError if anything is wrong.  We'll steal
    # the message from the TypeError.

    try:
        b = task.sig.bind(**params)
        b.apply_defaults()
        return b, cmdline
    except TypeError as ex:
        sys.exit('Task %s: %s' % (task.name, ex))


def _parse_double_dash(task, cmdline, params):
    """
    Parses a "--arg" token.

    The cmdline for this argument are removed from the front of cmdline.  (The first token is
    the name of the option.  The second token may be the value.)
    """
    name  = cmdline.pop(0)[2:]
    value = inspect.Parameter.empty

    value_provided = ('=' in name)

    if value_provided:
        name, value = name.split('=', 1)

    paramname = name.replace('-', '_')

    param = task.sig.parameters.get(name)

    if not param and name.startswith('no-'):
        # If a parameter was defined as "arg=True" then we accept "--no-arg" to set the
        # value to False.
        p = task.sig.parameters.get(paramname[3:])
        if p and p.default in (True, False):
            paramname = paramname[3:]
            params[paramname] = False
            return

    if not param:
        sys.exit('Task %s does not accept an argument %r' % (task.name, name))

    if value_provided and param.default in (True, False):
        sys.exit('Task %s argument %s does not accept a value' % (task.name, name))

    if value is inspect.Parameter.empty:
        # An '=' was not provided, so we need to determine if (1) this is a Boolean
        # parameter or (2) if the next token is the value.  (We've already handled the
        # --no-xxx version.)

        if param.default is False:
            value = True
        elif param.default is True:
            # This isn't necessary, but we'll take it since it may help scripts.  The user has
            # set the default to True for something, but supplied the same flag again.
            value = True
        else:
            # The next token needs to be the value.
            if not cmdline:
                sys.exit('Task %s argument %s was not provided a value' % (task.name, name))
            value = cmdline.pop(0)

    if name in 'args':
        sys.exit('Task %s argument %s parameter was specified more than once.' % (task.name, name))

    params[paramname] = value


def _parse_equals(task, cmdlline, params):
    """
    Parse a "name=value" arg token.

    The tokens for this argument are removed from the front of cmdlline.  (The first token is
    the name of the option.  The second token may be the value.)
    """
    name, value  = cmdlline.pop(0).split('=', 1)

    paramname = name.replace('-', '_')
    param = task.sig.parameters.get(name)

    if not param:
        sys.exit('Task %s does not accept an argument %r' % (task.name, name))

    if value and param.default in (True, False):
        sys.exit('Task %s argument %s does not accept a value' % (task.name, name))

    params[paramname] = value


def _parse_flags(task, cmdline, params):
    """
    Parse "-fx value" type arguments and write their values into `params`.

    Removes parsed tokens from `cmdline`.
    """
    # Each flag is a single-letter.
    #
    # For each flag, make sure we recognize it.  (The allowed flags have already been
    # determined by the task.)
    #
    # If the flag matches a Boolean parameter, the value is True.
    #
    #   -xyz   # Three flags all set to True
    #
    # Otherwise the flag requires a parameter and must be last in the argument or must be
    # followed by an equals sign:
    #
    #   -w=Bob
    #   -w Bob
    #
    #   -xyzw=Bob # Three flags plus -w set to Bob
    #   -xyzw Bob # Three flags plus -w set to Bob

    flags = cmdline.pop(0)[1:] # remove the leading dash

    for i, flag in enumerate(flags):
        name = task.flags.get(flag)
        if not name:
            sys.exit('Task %s does not accept a -%r flag' % (task.name, flag))

        param = task.sig.parameters[name]
        if param.default in (True, False):
            params[name] = True
            continue

        # This requires a value, so it must either be last so we use the next cmdline token or
        # it must be followed by '='.

        if i == len(flags)-1:
            if not cmdline:
                sys.exit('Task %s -%r flag was not provided a value' % (task.name, flag))
            params[name] = cmdline.pop(0)
            return

        if flags[i+1] != '=':
            sys.exit('Task %s -%r flag was not provided a value' % (task.name, flag))

        params[name] = flags[i+2:]
        return
