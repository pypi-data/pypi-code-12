import psycopg2
import pytest
import sys
from schema_migrations import MigrationController, STATUS_OK, STATUS_PENDING


@pytest.fixture(scope='session')
def databases(request):
    db_base = 'schema_migrations_{0}{1}{2}'.format(*sys.version_info)
    database_names = [
        '{0}_{1}'.format(db_base, i) for i in range(3)
    ]
    def create():
        conn = psycopg2.connect(
            user='postgres'
        )
        conn.set_isolation_level(0)
        cur = conn.cursor()
        for db in database_names:
            cur.execute('CREATE DATABASE {name}'.format(name=db))
        conn.close()

    def drop():
        conn = psycopg2.connect(
            user='postgres'
        )
        conn.set_isolation_level(0)
        cur = conn.cursor()
        for db in database_names:
            cur.execute('DROP DATABASE IF EXISTS {name}'.format(name=db))
        conn.close()

    drop()
    create()

    request.addfinalizer(drop)

    return {
        name:'postgresql://postgres@localhost:5432/{name}'.format(name=name)
        for name in database_names
    }


class TestSchemaMigrations:
    def test_migrations(self, databases):
        groups = dict(
            test='./tests/migrations/'
        )
        mc = MigrationController(databases=databases, groups=groups)

        migrations = mc.list()['test'] # test group
        assert len(migrations) == 2
        for m in migrations:
            assert m['status']['all'] == STATUS_PENDING
            dbs = m['status']['databases']
            assert len(dbs.keys()) == 3

            for db_status in dbs.values():
                assert db_status == False

        mc.migrate()
        mc.close()

        mc2 = MigrationController(databases=databases, groups=groups)

        migrations = mc2.list()['test'] # test group
        assert len(migrations) == 2
        for m in migrations:
            assert m['status']['all'] == STATUS_OK
            dbs = m['status']['databases']
            assert len(dbs.keys()) == 3

            for db_status in dbs.values():
                assert db_status == True

        mc2.close()
