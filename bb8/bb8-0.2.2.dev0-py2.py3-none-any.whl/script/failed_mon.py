import click as click
import yaml
from bb8.process import get_return_code
from bb8.script.config import default_config_file


@click.command('failed-mon', help='Run check, if failed, run ')
@click.option('--check', 'check_only', is_flag=True, help='Check then exit')
@click.option('--config', '-c', 'config_file', default=default_config_file, help='Path to config file')
def failed_monitor(config_file, check_only):
    data = yaml.load(open(config_file))
    items = data['failed-monitor']
    for item in items:
        check_name = item['name']
        check_return_code, check_out = get_return_code(item['check'])

        if check_return_code:
            print("Check {0}: FAILED ({1}). Out: {2}".format(check_name, check_return_code, check_out))

            if check_only:
                continue

            print("Run {0}".format(item['failed']))
            failed_rc, failed_out = get_return_code(item['failed'])
            if failed_rc:
                print("Run failed command FAILED. {0}".format(failed_out))

            print(failed_out)
        else:
            print("Check {0}: PASSED".format(check_name))
    # print(data)
