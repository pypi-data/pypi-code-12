import logging
import io
import os
from unittest import TestCase

import portend
from jaraco.postgres import PostgresDatabase, PostgresServer


HOST = os.environ.get('HOST', 'localhost')


def __setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    root.addHandler(handler)
__setup_logging()


class PostgresServerTest(TestCase):
    def test_serves_postgres(self):
        port = portend.find_available_local_port()
        server = PostgresServer(HOST, port)
        server.initdb()

        try:
            server.start()
            version = server.get_version()

            self.assertGreater(len(version), 0)
            self.assertGreaterEqual(version[0], 8)
        finally:
            server.destroy()

    def test_serves_postgres_with_locale(self):
        port = portend.find_available_local_port()
        server = PostgresServer(HOST, port)
        locale = 'C'
        server.initdb(locale=locale)

        try:
            server.start()
            server.get_version()  # To check we're able to talk to it.

            config = os.path.join(server.base_pathname, 'postgresql.conf')
            with io.open(config, encoding='utf-8') as f:
                for line in f:
                    if 'lc_messages =' in line:
                        self.assertIn(locale, line)
        finally:
            server.destroy()


class PostgresDatabaseTest(TestCase):
    def setUp(self):
        self.port = portend.find_available_local_port()
        self.server = PostgresServer(HOST, self.port)
        self.server.initdb()
        self.server.start()

    def tearDown(self):
        self.server.destroy()

    def test_creates_user_and_database(self):
        database = PostgresDatabase(
            'tests', user='john', host=HOST, port=self.port)

        database.create_user()
        database.create()

        rows = database.sql('SELECT 1')

        self.assertEqual(rows, [(1, )])
