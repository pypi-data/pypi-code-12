from rancon.tools import fail

import importlib as il
from argparse import ArgumentParser as AP
from os import environ
from collections import defaultdict

args = None
backend = None
source = None


def _parse_params_opts_env(env_name):
    opts = environ.get(env_name, None)
    if opts:
        return opts.split(",")
    else:
        return []


def _collapse_options(opts):
    """
    Takes a list of 'key=value' strings, and creates a dictionary of the form
    {'key' : 'value'}. If 'key' is present multiple times, the dictionary will
    contain a list with all values under the 'key' key.
    :param opts: A list of strings of the form 'key=val'
    :return: None
    """
    list_opts = [d.split("=", 1) for d in opts]
    tmp = defaultdict(list)
    for k, v in list_opts:
        tmp[k].append(v)
    for k, v in tmp.items():
        tmp[k] = v[0] if len(v) == 1 else v
    return dict(tmp)


def parse_params(sys_argv):
    global args
    global backend
    global source
    parser = AP()
    parser.add_argument("source",
                        help="Which source to use. Available are: 'rancher'. "
                             "Default: $RANCON_SOURCE or 'rancher'",
                        default=environ.get("RANCON_SOURCE", None))
    parser.add_argument("backend",
                        help="Which service backend (registry) to use. "
                             "Available are: 'consul'. "
                             "Default: $RANCON_BACKEND",
                        default=environ.get("RANCON_REGISTRY", None))
    parser.add_argument("-s", "--source-option",
                        help="Specify options for the available sources using "
                             "the format 'a=b'. "
                             "Default: $SOURCE_OPTIONS (which should look "
                             "like 'O1=V1,O2=V2,...')",
                        action="append",
                        default=_parse_params_opts_env('FRONTEND_OPTIONS '))
    parser.add_argument("-b", "--backend-option",
                        help="Specify options for the available registries "
                             "using the format 'a=b'. "
                             "Default: $REGISTRY_OPTIONS (which should look "
                             "like 'O1=V1,O2=V2,...')",
                        action="append",
                        default=_parse_params_opts_env('BACKEND_OPTIONS'))
    parser.add_argument("-i", "--id",
                        help="Instance ID of this process, used 'garbage "
                             "collecting' services which are no longer present,"
                             "in case of multiple rancon instances which see "
                             "different services. Default: $RANCON_ID or "
                             "'default'",
                        default=environ.get('RANCON_ID', 'default'))
    parser.add_argument("-c", "--continuous",
                        help="Continuous mode - keep running and perform "
                             "regular updates. Use -w to configure update wait "
                             "intervals. "
                             "Default: $RANCON_FOREGROUND (presence of env "
                             "variable is true, the setting does not matter), "
                             "or False",
                        action='store_true',
                        default=bool(environ.get("RANCON_FOREGROUND", False)))
    parser.add_argument("-w", "--wait",
                        help="How many seconds to wait between runs if -f is "
                             "used. Default: $RANCON_WAIT or 5",
                        type=int,
                        default=int(environ.get("RANCON_WAIT", "5")))

    args = parser.parse_args(sys_argv)
    errors = []

    # get parameters
    args.backend_options = _collapse_options(args.backend_option)
    args.source_options = _collapse_options(args.source_option)
    del args.backend_option
    del args.source_option

    # check required SOURCE and REGISTRY settings
    classes = []
    for a in (("source", args.source, "-s", args.source_options),
              ("backend", args.backend, "-b", args.backend_options)):
        try:
            i = il.import_module("rancon.{}s.{}".format(a[0], a[1]))
            got_class = i.get()
            for ropt in got_class.required_opts:
                if ropt not in a[3]:
                    errors.append("Missing option for {} '{}': {} {}=..."
                                  .format(a[0], a[1], a[2], ropt))
        except ImportError:
            errors.append("Invalid source type: {}".format(a[1]))

        for opt in a[3].keys():
            if not (opt in got_class.required_opts or
                    opt in got_class.additional_opts):
                errors.append("Unkonwn option for {} '{}': {}"
                              .format(a[0], a[1], opt))

        if len(errors) == 0:
            classes.append(got_class(**a[3]))

    if errors:
        fail(errors)
    else:
        source, backend = classes[0], classes[1]
