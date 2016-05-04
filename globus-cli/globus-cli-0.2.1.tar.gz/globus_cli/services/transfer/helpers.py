from __future__ import print_function
import click
import json

from globus_sdk import TransferClient

from globus_cli import version
from globus_cli.helpers import print_table


def get_client():
    return TransferClient(app_name=version.app_name)


def display_name_or_cname(ep_doc):
    return ep_doc['display_name'] or ep_doc['canonical_name']


def print_json_from_iterator(iterator):
    json_output_dict = {'DATA': []}
    for item in iterator:
        dat = item
        try:
            dat = item.data
        except AttributeError:
            pass
        json_output_dict['DATA'].append(dat)
    print(json.dumps(json_output_dict, indent=2))


def endpoint_list_to_text(iterator):
    print_table(iterator, [('Owner', 'owner_string'), ('ID', 'id'),
                           ('Display Name', display_name_or_cname)])


def assemble_generic_doc(datatype, *args, **kwargs):
    doc = {'DATA_TYPE': datatype}
    for argname in kwargs:
        if kwargs[argname] is not None:
            doc[argname] = kwargs[argname]
    return doc


def endpoint_id_option(*args, **kwargs):
    def decorate(f, **kwargs):
        """
        Work of actually decorating a function -- wrapped in here because we
        want to dispatch depending on how this is invoked
        """
        help = kwargs.get('help', 'ID of the Endpoint')
        f = click.option('--endpoint-id', required=True, help=help)(f)
        return f

    # special behavior when invoked with only one non-keyword argument: act as
    # a normal decorator, decorating and returning that argument with
    # click.option
    if len(args) == 1 and len(kwargs) == 0:
        return decorate(args[0])

    # if we're not doing that, we should see no positional args
    # the alternative behavior is to fall through and discard *args, but this
    # will probably confuse someone in the future when their arguments are
    # silently discarded
    elif len(args) != 0:
        raise ValueError(
                'endpoint_id_option() cannot take positional args')

    # final case: got 0 or more kwargs, no positionals
    # do the function-which-returns-a-decorator dance to produce a
    # new decorator based on the arguments given
    else:
        def inner_decorator(f):
            return decorate(f, **kwargs)
        return inner_decorator
