# -*- coding: utf-8 -*-
"""A tool to generate key remap configuration for Karabiner

Usage:
    easy_karabiner [-evrl] [SOURCE] [TARGET | --string]
    easy_karabiner [--help | --version]
"""
from __future__ import print_function
import os
import sys
import lxml
import click
from subprocess import call
from . import __version__
from . import util
from . import query
from . import config
from . import exception
from .osxkit import get_all_peripheral_info
from .basexml import BaseXML
from .generator import Generator
from .fucking_string import *


@click.command()
@click.help_option('--help', '-h')
@click.version_option(__version__, '--version', '-v', message='%(version)s')
@click.argument('inpath', default=config.get_default_config_path(), type=click.Path())
@click.argument('outpath', default=config.get_default_output_path(), type=click.Path())
@click.option('--verbose', '-V', help='Print more text.', is_flag=True)
@click.option('--string', '-s', help='Output as string.', is_flag=True)
@click.option('--reload', '-r', help='Reload Karabiner.', is_flag=True)
@click.option('--no-reload', help='Opposite of --reload', is_flag=True)
@click.option('--edit', '-e', help='Edit default config file.', is_flag=True)
@click.option('--list-peripherals', '-l', help='List name of all peripherals.', is_flag=True)
def main(inpath, outpath, **options):
    """
    \b
    $ easy_karabiner
    $ easy_karabiner input.py output.xml
    $ easy_karabiner input.py --string
    """
    config.set(options)

    if config.get('help') or config.get('version'):
        return
    elif config.get('edit'):
        edit_config_file()
    elif config.get('list_peripherals'):
        list_peripherals()
    elif config.get('reload'):
        reload_karabiner()
    else:
        try:
            configs = read_config_file(inpath)
            xml_str = gen_config(configs)

            if config.get('string'):
                print_message(xml_str)
            else:
                try:
                    if not is_generated_by_easy_karabiner(outpath):
                        backup_file(outpath)
                except IOError:
                    pass
                finally:
                    write_generated_xml(outpath, xml_str)
                    if is_need_reload(config.get('reload'), config.get('no_reload'), outpath):
                        reload_karabiner()

            show_config_warnings()
        except exception.ConfigError as e:
            print_error(e)
            sys.exit(1)
        except IOError as e:
            print_error("%s not exist" % e.filename)
            sys.exit(1)
        except Exception as e:
            print_error(e)
            sys.exit(1)

    sys.exit(0)


def read_config_file(config_path):
    if config.get('verbose'):
        print_info('Execute "%s"' % config_path)
    return util.read_python_file(config_path)


def write_generated_xml(outpath, content):
    if config.get('verbose'):
        print_info('Write XML to "%s"' % outpath)
    write_utf8_to(content, outpath)


def edit_config_file():
    click.edit(filename=config.get_default_config_path())


def is_need_reload(reload, no_reload, outpath):
    if no_reload:
        return False
    else:
        return reload or (outpath == config.get_default_output_path())


def reload_karabiner():
    NOTIFICATION_MSG = "Enabled generated configuration"
    NOTIFICATION_CMD = ('/usr/bin/osascript', '-e',
                        'display notification "%s" with title "Karabiner Reloaded"' % NOTIFICATION_MSG)
    KARABINER_CMD = config.get_karabiner_bin('karabiner')

    if config.get('verbose'):
        print_info("Reload Karabiner config")
    call([KARABINER_CMD, 'enable', 'private.easy_karabiner'])
    call([KARABINER_CMD, 'reloadxml'])
    call(NOTIFICATION_CMD)


def list_peripherals():
    peripheral_names = [ensure_utf8(name) for name in get_all_peripheral_info().keys()]
    for name in sorted(peripheral_names):
        print_message(name)


def gen_config(configs):
    maps = configs.get('MAPS')
    definitions = configs.get('DEFINITIONS')
    query.update_aliases(configs)
    if config.get('verbose'):
        print_info("Generate XML configuration")
    return Generator(maps, definitions).to_str()


def is_generated_by_easy_karabiner(filepath):
    try:
        tag = BaseXML.parse(filepath).find('Easy-Karabiner')
        return tag is not None
    except lxml.etree.XMLSyntaxError:
        return False


def backup_file(filepath, new_path=None):
    with open(filepath, 'rb') as fp:
        if new_path is None:
            # private.xml -> private.941f123.xml
            checksum = util.get_checksum(fp.read())
            parts = os.path.basename(filepath).split('.')
            parts.insert(-1, checksum)
            new_name = '.'.join(parts)

            if config.get('verbose'):
                print_info("Backup original XML config file")
            new_path = os.path.join(os.path.dirname(filepath), new_name)

        os.rename(filepath, new_path)
        return new_path


def show_config_warnings():
    records = exception.ExceptionRegister.get_all_records()
    for raw_data, e in records:
        exception_class = type(e)

        if exception_class == exception.UndefinedFilterException:
            msg = 'Undefined filter'
        elif exception_class == exception.UndefinedKeyException:
            msg = 'Undefined key'
        elif exception_class == exception.InvalidDefinition:
            msg = 'Invalid definition'
        elif exception_class == exception.InvalidKeymapException:
            msg = 'Invalid keymap'
        else:
            msg = exception_class.__name__

        if len(e.args) == 0:
            print_warning('%s: %s' % (msg, raw_data))
        elif len(e.args) == 1:
            print_warning('%s: `%s` in %s' % (msg, e.args[0], raw_data))
        else:
            print_warning('%s: %s in %s' % (msg, e.args, raw_data))


def print_message(msg, color=None, err=False):
    """Seems `click.echo` has fixed the problem of UnicodeDecodeError when redirecting (See
    https://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
    for detail). As a result, the below code used to solve the problem is conflict with `click.echo`.
    To avoid the problem, you should always use `print` with below code or `click.echo` in `__main__.py`

        if sys.version_info[0] == 2:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
        else:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    """
    click.secho(msg, fg=color, err=err)


def print_error(msg):
    print_message(msg, color='red', err=True)


def print_warning(msg):
    print_message(msg, color='yellow', err=True)


def print_info(msg):
    print_message(msg, color='green')
