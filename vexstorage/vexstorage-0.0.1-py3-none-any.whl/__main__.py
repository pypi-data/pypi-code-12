import os
import argparse
from os import path

import yaml

from vexstorage.messaging import Messaging
from vexstorage.database import DatabaseManager, create_database


def main(database_file, settings_filepath):
    database = DatabaseManager(database_file)

    with open(settings_filepath) as f:
        settings = yaml.load(f)

    # alias the sockets to connect to for pep8 reasons
    _s = 'sockets_to_connect_to'
    sockets_to_connect_to = settings[_s]

    # FIXME
    messaging = Messaging(sockets_to_connect_to)

    run(database, messaging)


def run(database, messaging):
    while True:
        frame = messaging.sub_socket.recv_pyobj()

        if len(frame) == 4:
            service = frame[0]
            author = frame[2]
            text = frame[3]
            database.record_message(service, author, text)


def _get_kwargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database_filepath',
                        action='store',
                        default='')

    parser.add_argument('--create_database',
                        action='store',
                        default=False)

    parser.add_argument('--settings_filepath',
                        action='store')

    return vars(parser.parse_args())


if __name__ == '__main__':
    kwargs = _get_kwargs()
    database_filepath = kwargs['database_filepath']

    if not database_filepath:
        vexdir = path.join(path.expanduser('~'), '.vexbot')
        if not path.isdir(vexdir):
            os.mkdir(vexdir)
        database_filepath = path.join(vexdir, 'message_storage.db')

    if kwargs['create_database']:
        create_database(database_filepath)

    settings_filepath = kwargs['settings_filepath']

    if settings_filepath:
        main(database_filepath,
             settings_filepath)
