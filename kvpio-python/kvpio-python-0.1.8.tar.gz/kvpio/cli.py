"""
kvpio cli
---------
The command-line application for [kvp.io](https://www.kvp.io)

Basic bucket usage:

    $ export KVPIO_APIKEY=<your api key here>
    $ kvpio bucket set foo bar
    $ kvpio bucket get foo
    bar

Bucket with nested data:

    $ kvpio bucket set foo '{"bar": {"baz": 123}}'
    $ kvpio bucket get foo/bar/baz
    123

Basic template usage:

    $ kvpio template set foo 'baz is equal to {{ foo.bar.baz }}'
    $ kvpio template get foo
    baz is equal to 123

Get account information:

    $ kvpio account
    {"id": "kvp.io", "email": "support@kvp.io", "reads": 87, "size": 124}

- `copyright` (c) 2016 by Steelhive, LLC
- `license` MIT, see LICENSE for more details
"""

import os
import sys
import json
import click
import kvpio


version = '0.1.8'


def print_result(result):
    code, response = result
    if code == 200:
        sys.stdout.write(response + '\n')
    else:
        sys.stderr.write(response + '\n')


@click.group()
@click.version_option(version=version)
def cli():
    """

        kvpio account

        kvpio bucket    list | get | set | del

        kvpio template  list | get | set | del

    To get help on commands and sub-commands, type:

        kvpio <command> --help

        kvpio <command> <sub-command> --help
    """

    api_key = os.environ.get('KVPIO_APIKEY', None)
    if not api_key:
        api_key_file = '{}/.kvpio'.format(os.path.expanduser('~'))
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
    if not api_key:
        print(
            '\n' +
            'WARNING: No api key was provided. This means only READ \n' +
            'operations will be permitted on PUBLIC endpoints. You can \n' +
            'set an API key via the following:\n' +
            '    as an environment variable named KVPIO_APIKEY\n' +
            '    as a single line in the file ~/.kvpio\n'
        )
    kvpio.api_key = api_key

#
# bucket commands
#
@cli.command('account')
def account():
    """
    Get account information.
    """
    if not kvpio.api_key:
        click.echo('Please provide an API key.')
        return
    print_result(
        kvpio.Account().get()
    )

#
# bucket commands
#
@cli.group('bucket')
def bucket():
    """
    Interact with key/value pairs.
    """

@bucket.command('list')
def bucket_list():
    """
    Retrieve a list of keys.
    """
    print_result(
        kvpio.Bucket().list()
    )

@bucket.command('get')
@click.argument('key')
def bucket_get(key):
    """
    Retrieve the value stored at KEY.

    KEY may be a single word or a path of the form path/to/key to access
    nested values.
    """
    print_result(
        kvpio.Bucket().get(key)
    )

@bucket.command('set')
@click.argument('key')
@click.argument('value', required=False)
@click.option('--file', type=click.File('rb'), help='A file path from which data is read.')
def bucket_set(key, value, file):
    """
    If VALUE is specified, set KEY to the specified literal value.

    If --file is specified, set KEY to the data in FILENAME.

    KEY may be a single word or a path of the form path/to/key to set
    nested values.
    """
    if file:
        try:
            value = json.loads(file.read().decode('utf-8'))
        except Exception as e:
            sys.exit(
                'An error occured while reading the file: {}'.format(str(e))
            )
        kvpio.Bucket().set(key, value)
    else:
        try:
            value = json.loads(value)
        except:
            pass
        kvpio.Bucket().set(key, value)


@bucket.command('del')
@click.argument('key')
def bucket_del(key):
    """
    delete KEY and it's value

    KEY may be a single word or a path of the form path/to/key to delete.
    KEY and all keys and values nested below it will be deleted.
    """
    kvpio.Bucket().delete(key)

#
# template comands
#
@cli.group('template')
def template():
    """
    Interact with templates.
    """

@template.command('list')
def template_list():
    """
    Retrieve a list templates.
    """
    print_result(
        kvpio.Templates().list()
    )

@template.command('get')
@click.argument('name')
@click.option('--data', help='A dictionary, as a JSON string.')
@click.option('--raw', is_flag=True, help='Return the template un-rendered.')
def template_get(name, data, raw):
    """
    Retrieve and render the template at NAME

    Values for the template are retrieved from your bucket based on variable
    names found in template.

    If the --data option specifics valid JSON data, it's values will override
    those found in the bucket. This is useful for rendering templates with
    non-persistent, one-time values.

    If the --raw flag is specified, the original, un-rendered template is
    returned.
    """
    try:
        data = json.loads(data)
    except:
        data = None
    if raw:
        print_result(
            kvpio.Templates().get(name, raw=raw)
        )
    else:
        print_result(
            kvpio.Templates().get(name, data=data)
        )

@template.command('set')
@click.argument('name')
@click.argument('template')
def template_set(name, template):
    """
    Set NAME to the specified template TEMPLATE.

    TEMPLATE must be a string, optionally using the Jinja2 template language.
    """
    kvpio.Templates().set(name, template)

@template.command('del')
@click.argument('name')
def template_del(name):
    """
    Delete NAME and it's template.
    """
    kvpio.Templates().delete(name)
