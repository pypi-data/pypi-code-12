"""
TODO:
1. Monitor change of files in path
2. Upload change to github
"""
import logging
from time import time

import click as click
import yaml
from bb8.container import bb8, git_push
from bb8.monitor import FileMonitor, FileMonitorPool, MonAndRun

config_file = 'bb8.yml'

paths = []


def load_paths():
    global paths

    config = yaml.load(open(config_file))
    paths = config['paths']


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli():
    pass


@click.command('sync', help='Copy change files and push to git')
def sync_files():
    # Init monitor
    def sync_and_push(path=None):
        start = time()

        with click.progressbar(length=2,
                               label='Copy files and push to git') as bar:

            change = bb8.sync_paths(paths)
            bar.update(1)

            if change:
                git_push.commit_and_push()
                bar.update(2)

            if change:
                print('\nSynced in %s seconds' % (time() - start))
            else:
                print('\nSync: no change')

    # monitor paths
    paths_monitor = FileMonitor(sync_and_push)

    def on_config_change(path=None):
        print('config change')

        # Reload paths
        load_paths()

        # Update watch files
        paths_monitor.watch_multiple(bb8.get_monitor_files(paths))

        # Trigger sync and push
        sync_and_push()

    # Reload paths
    load_paths()

    # Update watch files
    paths_monitor.watch_multiple(bb8.get_monitor_files(paths))

    # Monitor config_file
    config_monitor = FileMonitor(on_config_change)
    config_monitor.watch(config_file)

    file_monitor_pool = FileMonitorPool()
    file_monitor_pool.add_file_monitor(config_monitor)
    file_monitor_pool.add_file_monitor(paths_monitor)

    print("Wait for file change")
    file_monitor_pool.start()


@click.command('mon', help='Monitor files and run commands when change')
@click.option('--config', '-c', 'config_file', default='bb8.yml', help='Path to config file')
def mon_and_run(config_file):
    mon = MonAndRun(config_file)
    mon.start()


cli.add_command(sync_files)
cli.add_command(mon_and_run)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    cli()
