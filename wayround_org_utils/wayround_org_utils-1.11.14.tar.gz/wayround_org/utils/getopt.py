
import logging


def getopt(args):
    """
    Parser as command line arguments and options

    It's not compatible with CPython getopt module. It's work differently in
    many ways.

    Parameter must be list of strings: Simple sys.argv will go.

    Example:

       getopt.getopt(['a', 'b', 'c', 'd=123', 'dd=123', '-a',
                       '3', '-b=3', '--c=4', '--long=5',
                       '---strange=6', '--', '-e=7'])

       ([('-a', None),
         ('-b', '3'),
         ('--c', '4'),
         ('--long', '5'),
         ('---strange', '6')],
        ['a', 'b', 'c', 'd=123', 'dd=123', '3', '-e=7'])

    """

    # TODO: add '--' delimiter support

    ret_args = []
    ret_opts = []

    if not isinstance(args, list):
        raise TypeError

    all_args = False

    len_args = len(args)

    i = 0

    while True:

        if i == len_args:
            break

        if all_args:

            ret_args.append(args[i])

        else:

            args_i_len = len(args[i])

            if args_i_len > 1:

                if args[i] == '--':
                    all_args = True
                else:

                    if args[i].startswith('-'):

                        eq_pos = args[i].find('=')
                        if eq_pos != -1:
                            ret_opts.append(
                                (args[i][:eq_pos], args[i][eq_pos + 1:])
                                )
                        else:
                            ret_opts.append((args[i], None))

                    else:
                        ret_args.append(args[i])

            else:
                ret_args.append(args[i])

        i += 1

    return ret_opts, ret_args


def getopt_keyed(args):
    opts, args = getopt(args)

    opts_k = {}
    for i in opts:
        opts_k[i[0]] = i[1]

    return opts_k, args


def _opt_strip(opt):
    return opt.lstrip('!').rstrip('=')


def _opts_strip(opts_list):

    ret = []

    for i in opts_list:
        ret.append(_opt_strip(i))

    return ret


def check_options(opts, opts_list, mute=False):
    """
    opts - list of opts returned by getopt (i.e.)
    opts_list - list of acceptable options:
          starting with '!' - required option
          ending with '=' - must have parameter

    return: int - error count
    """

    ret = 0

    for i in opts:
        if not i in _opts_strip(opts_list):

            if not mute:
                logging.error("option not supported: {}".format(i))

            ret += 1

    for i in opts_list:

        i_stripped = _opt_strip(i)

        required = i.startswith('!')
        value_required = i.endswith('=')

        if required and not i_stripped in opts:

            if not mute:
                logging.error(
                    "required parameter absent: {}".format(i_stripped)
                    )

            ret += 1

        if i_stripped in opts:
            if value_required and opts[i_stripped] is None:

                if not mute:
                    logging.error(
                        "parameter `{}' must have value".format(i_stripped)
                        )

                ret += 1

    return ret
