from __future__ import unicode_literals
import time
from pathlib import Path
import os
import re
import importlib

package = 'amigrations'


def _get_all_migrations_from_folder(migration_folder):
    """Simply checks folder for files which ends with up.sql

    :param migration_folder: Path to migration folder
    :type migration_folder: string
    :returns: Path object globbed for a string *.up.sql
    :rtype: pathlib.Path
    """

    return Path(migration_folder).glob("*.up.sql")


def _transform_file_name_to_migration_name(name):
    """extracts from filename migration name

    :param name: filename
    :type name: string
    :returns: Transformed filename
    :rtype: string
    """

    return re.sub(r'\.(up|down)\.sql$', '', name)


class AMigrations(object):

    def __init__(self, db_uri, migration_folder, current_package=None,
                 table_name='migrations', supported_packages=()):
        """Initializes object

        :param db_uri: An uri formed in a format like
        sqlite+pysqlite:///path_to_file.
        This is a format well known for most of the developers.
        :type db_uri: string
        :param migration_folder: path to the folder with migrations
        :type migration_folder: string
        :param current_package: we want to support a migrations done in
        different projects.
        It would let us to decouple a python project into few
        independent projects which
        decouples tests as well, making more easy to reuse functionality
        in another projects, The migrations for another project should be in
        the same `migration_folder`, so in theory we can symlink another folder
        into `migration_folder`
        :type current_package: string
        :param supported_packages: the list of the packages to be supported in
        migration tool
        :type supported_packages: tuple|list
        :returns: None
        :rtype: None
        """
        self.db_uri = db_uri
        self.migration_folder = migration_folder
        self.current_package = (current_package if current_package in
                                supported_packages else None)
        self.supported_packages = supported_packages
        if not os.path.exists(migration_folder):
            os.makedirs(migration_folder)
        self.table_name = table_name

    def create(self, message):
        """Creates migration

        :param message: An explanation what is the migration about
        :type message: string
        :returns: returns a dict with keys up/down. Values are
        pathlib.Path objects
        :rtype: {'up': pathlib.Path, 'down': pathlib.Path}
        """
        timestamp = str(int(time.time()))
        s_message = re.sub(r'\s', '_', message[:30])
        base_filename = timestamp + "_" + s_message + ".{}.sql"
        suffix_to_messages = {
            'up': "/**Up migration\n{}**/".format(message),
            'down': "/**Down migration\n{}**/".format(message)
        }
        files = {}
        migration_folder = self.migration_folder
        if self.current_package:
            migration_folder += "/" + self.current_package + "/"
            if not os.path.exists(migration_folder):
                os.makedirs(migration_folder)
        for suffix in ('up', 'down'):
            _filepath = Path(migration_folder, base_filename.format(suffix))
            with _filepath.open('w') as fp:
                fp.write(suffix_to_messages[suffix])
            print("Added {}".format(_filepath))
            files[suffix] = _filepath
        return files

    @property
    def _adapter(self):
        """Returns adapted to the database specified in db uri
        :returns: Adapted specified in the db uri
        :rtype: amigrations.adapter.postgresql.Adapter
        """
        adapter = self.db_uri.split(':')[0].split('+')[0]
        return getattr(importlib.import_module(
            '.adapters.' + adapter,
            package=package
        ), 'Adapter')(self.db_uri, self.table_name)

    def upgrade(self):
        """Looks for migration files not applied before

        :returns: None
        :rtype: None
        """
        adapter = self._adapter
        migrations = _get_all_migrations_from_folder(self.migration_folder)
        all_migrations = {migration.name: {
            'package': 'main',
            'migration': migration
        } for migration in migrations}
        if self.supported_packages:
            for package in self.supported_packages:
                package_migrations = _get_all_migrations_from_folder(
                    self.migration_folder + "/" + package + "/"
                )
                all_migrations.update({
                    migration.name: {
                        'package': package,
                        'migration': migration
                    } for migration in package_migrations
                })

        sorted_migrations = sorted(all_migrations.keys())
        applied_migrations = adapter.get_applied_migrations()
        for _migration in sorted_migrations:
            migration_name = _transform_file_name_to_migration_name(_migration)
            if migration_name in applied_migrations:
                continue
            migration_data = all_migrations[_migration]
            adapter.apply(
                migration_name,
                migration_data['migration'],
                migration_data['package']
            )

    def downgrade_to(self, downgrade_to):
        """Downgrade database to the migration id: `downgrade_to`

        :param downgrade_to: An id the database will be downgraded to
        :returns: None
        :rtype: None
        """
        adapter = self._adapter
        applied_migrations = adapter.get_migrations_to_downgrade(downgrade_to)
        for _migration_to_downgrade in applied_migrations:
            migration_name, migration_id, package = _migration_to_downgrade
            migration_folder = self.migration_folder
            if package != 'main' and package in self.supported_packages:
                migration_folder += "/" + package + "/"
            _migration = Path(migration_folder, migration_name + ".down.sql")
            adapter.downgrade(migration_id, _migration)
