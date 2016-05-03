#!/usr/bin/env python3
# use absolute imports to allow pycharm to run/debug
import click
import sys
from magerestore.app import Magerestore


pass_app = click.make_pass_decorator(Magerestore)
CLI_OPTIONS = dict()


def validate_resource_name(ctx, param, value):
    names = ctx.obj.resource_manager.names()
    if value not in names:
        raise click.BadParameter("Invalid resource name `{value}` ({names})".format(value=value, names=', '.join(names)))
    return value


def exception_handler(exception):
    click.secho("Error: %s" % str(exception).strip('\''), err=True, fg='white', bg='red')
    if CLI_OPTIONS['DEBUG']:
        raise exception
    else:
        sys.exit(1)


@click.group()
@click.pass_context
@click.option('--debug', is_flag=True)
@click.option('--config', type=click.Path(dir_okay=False, exists=True), default='magerestore.json', help="Config file to use")
def main(ctx, debug, config):
    global CLI_OPTIONS
    CLI_OPTIONS['DEBUG'] = debug
    try:
        ctx.obj = Magerestore(config)
    except Exception as e:
        exception_handler(e)


@click.command()
@pass_app
@click.argument('resource', callback=validate_resource_name)
def restore(app, resource):
    resource = app.resource_manager.get_resource(resource)

    try:
        resource.pre_check()
        resource.get_file(get_file_callback)
    except Exception as e:
        exception_handler(e)

    resource.unpack()


def get_file_callback(got, total_size):
    func = get_file_callback
    if not hasattr(func, 'progressbar'):
        func.progressbar = click.progressbar(length=total_size, label="Getting resource file")
        func.last_got = 0

    progress = got - func.last_got
    func.last_got = got
    func.progressbar.update(progress)

main.add_command(restore)

if __name__ == '__main__':
    main()
