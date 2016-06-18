import os
import psycopg2
import yaml

from psycopg2._psycopg import ProgrammingError
try:
    from urllib.parse import urlsplit
except ImportError:  # pragma: no cover
    from urlparse import urlsplit


DEFAULT_GROUP = {'default': './migrations/'}
STATUS_PENDING = -1
STATUS_PARTIAL = 0
STATUS_OK = 1

SELECT_SQL = 'select group_name, name from migration_history'
INSERT_SQL = 'insert into migration_history values (%s, %s)'
CREATE_TABLE_DDL = '''
BEGIN;
CREATE TABLE migration_history (
  group_name TEXT NOT NULL,
  name TEXT NOT NULL,
  PRIMARY KEY (group_name, name)
);
END;
'''


class MissingDependency(Exception):
    def __init__(self, migration, dependency):
        super(MissingDependency, self).__init__(
            'Required dependency not found. {} requires {}'.format(
                migration, dependency
            )
        )


class MigrationController(object):

    def __init__(self, databases=None, groups=None):
        self._databases = databases or {}
        self._groups = groups or DEFAULT_GROUP
        self._connections = dict()
        self._completed = self.list_completed()

    def list_completed(self):
        return {
            db: self.list_completed_in_db(db)
            for db in self._databases.keys()
        }

    def list_completed_in_db(self, db):
        cur = self.get_cursor(db)
        completed = {}

        try:
            cur.execute(SELECT_SQL)
            for group, name in cur.fetchall() or []:
                if group not in completed:
                    completed[group] = []

                completed[group].append(name)
        except ProgrammingError:
            # Must rollback previous transaction
            cur.execute('ROLLBACK;')
            cur.execute(CREATE_TABLE_DDL)
        cur.close()

        return completed

    def list(self):
        return {
            k: self.list_group(k, f) for k, f in (self._groups or {}).items()
        }

    def list_group(self, group, group_folder):
        def group_migrations():
            previous_migration = None
            for migration in os.listdir(group_folder):
                migration_folder = os.path.join(group_folder, migration)
                if not os.path.isdir(migration_folder):
                    continue

                migration_info = self.migration_info(
                    group, migration, previous_migration
                )
                previous_migration = migration_info
                yield migration_info

        return list(group_migrations())

    def migration_plan(self):
        plan = []
        wait_list = []
        all_migrations = {}

        def missing_deps(key, strict=False):
            migration = all_migrations[key]
            deps = migration['dependencies']
            for dkey in deps:
                if strict and dkey not in all_migrations:
                    raise MissingDependency(key, dkey)
            return True in [
                d not in plan for d in deps
            ]

        for group, migrations in self.list().items():
            migrations = sorted(migrations, key=lambda k: k['name'])
            for migration in migrations:
                key = migration['key']
                all_migrations[key] = migration

                if missing_deps(key):
                    wait_list.append(key)
                else:
                    plan.append(key)

        while len(wait_list):
            for key in wait_list:
                if missing_deps(key, strict=True):
                    continue
                plan.append(key)
                del wait_list[wait_list.index(key)]

        return [all_migrations[key] for key in plan]

    def migrate(self):
        for migration in self.migration_plan():
            print('{group} {name}'.format(**migration))
            for db, status in migration['status']['databases'].items():
                print('    {db}: {status}'.format(
                    db=db,
                    status='OK' if status else 'Needs migration'
                ))
                if not status:
                    cur = self.get_cursor(db)
                    cur.execute('BEGIN;')
                    cur.execute(migration['forward'])
                    cur.execute(
                        INSERT_SQL,
                        (migration['group'], migration['name'])
                    )
                    cur.execute('END;')
                    print('    {db}: Done'.format(db=db))

    def migration_info(self, group, migration_name, previous_migration):

        def get_file_content(file):
            filepath = os.path.join(self._groups[group], migration_name, file)
            if not os.path.exists(filepath):
                return None

            with open(filepath) as f:
                return f.read()

        def get_config():
            config_yaml = get_file_content('.config.yml') or ''
            config = yaml.load(config_yaml) or {}

            if 'dependencies' in config:
                deps = config['dependencies']
                # If the configured dependency is a string, convert to a list
                # with the dependency as an element of the list
                if isinstance(deps, str):
                    config['dependencies'] = [deps]
            else:
                config['dependencies'] = []

            # Include previous migration as a dependency
            if previous_migration is not None:
                config['dependencies'].append(previous_migration['key'])

            return config

        def get_status():
            db_status = {
                db: self.is_migration_applied(group, migration_name, db)
                for db in (self._databases or {}).keys()
            }

            return dict(
                databases=db_status,
                all=STATUS_OK if False not in db_status.values() else
                STATUS_PARTIAL if True in db_status.values() else
                STATUS_PENDING
            )

        def get_script():
            return get_file_content('forward.sql') or ''

        info = get_config()
        info.update(dict(
            name=migration_name,
            group=group,
            key='{}:{}'.format(group, migration_name),
            status=get_status(),
            forward=get_script(),
        ))
        return info

    def is_migration_applied(self, group, migration, db):
        return migration in (self._completed or {}).get(db, {}).get(group, [])

    def get_cursor(self, db):
        return self.get_conn(db).cursor()

    def get_conn(self, db):
        if db not in self._connections:
            self._connections[db] = psycopg2.connect(
                **self.parse_pgurl(self._databases[db])
            )

        return self._connections[db]

    def parse_pgurl(self, url):
        """
        Given a Postgres url, return a dict with keys for user, password,
        host, port, and database.
        """
        parsed = urlsplit(url)

        return {
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
            'host': parsed.hostname,
            'port': parsed.port or 5432,
        }

    def close(self):
        for conn in self._connections.values():
            conn.close()
