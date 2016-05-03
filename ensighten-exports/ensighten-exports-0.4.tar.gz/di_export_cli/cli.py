from exports import Exports
from parser import Parser
import click
import os
from settings_handler import settings_are_valid, update_configuration


@click.group()
def cli():
    pass


@cli.command(help='Download new exports')
@click.option('--config_id', help='Your config id', required=True)
@click.option('--new_name', help='file name of log file for new files', default='NEW')
@click.option('--changed_name', help='file name of log file for new files', default='CHANGED')
@click.argument('path')
def sync(config_id, path, new_name, changed_name):
    if settings_are_valid():
        update_configuration()
        if os.path.exists(path):
            if new_name and changed_name:
                exports = Exports(config_id, path)
                exports.sync_files(new_name, changed_name)
            else:
                print "new_name or changed_name can not be empty strings."
        else:
            print "Specified path does not exist"


@cli.command(help='See status of export')
@click.option('--config_id', help='Your config id', required=True)
@click.option('--json', is_flag=True, help='Outputs the info in JSON format')
@click.argument('path')
def info(config_id, json, path):
    if settings_are_valid():
        update_configuration()
        if os.path.exists(path):
            exports = Exports(config_id, path)
            try:
                if json:
                    print exports.get_info_json()
                else:
                    print exports.get_info_readable()
            except Exception as e:
                print 'Unexpected error occured:'
                raise
        else:
            print "Specified path does not exist"


@cli.command(help='Convert json to csv')
@click.option('--header_value', '-h', multiple=True)
@click.option('--header/--no-header', default='True')
@click.argument('from_path')
@click.argument('to_path')
def convert(from_path, to_path, header_value, header):
    parser = Parser(from_path, to_path, header_value, header)
    parser.parse()


@cli.command(help='Verify credentials')
def verify():
    if settings_are_valid():
        update_configuration()
        export = Exports("", "")
        export.verify()


#  Click
if __name__ == '__main__':
    cli()
