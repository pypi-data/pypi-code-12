from datetime import datetime

from .uri import URI


class BaseAdapter(object):

    placeholder = '%s'

    def __init__(self, db_uri, table_name):
        """A base class for specific adapter classes like postgresql, sqlite, etc
        :param db_uri: A database uri.
        :type db_uri: string
        :param table_name: table name for migrations
        :type table_name: string
        :returns: None
        :rtype: None
        """
        self.db_uri = db_uri
        self.table_name = table_name
        self._ensure_db_has_migration_table()

    @property
    def _client(self):
        """Returns a connection to specific database

        :returns: connection to specific database

        """
        raise NotImplementedError

    def get_applied_migrations(self):
        """Gets a names of the migrations has been applied

        :returns: A list of all migrations applied
        :rtype: [string, string, ...]
        """
        sql = "SELECT name FROM {}".format(self.table_name)
        cursor = self._client.cursor()
        cursor.execute(sql)
        migrations = []
        for _row in cursor.fetchall():
            migrations.append(_row[0])
        return migrations

    @property
    def _uri(self):
        """Returns uri built on given uri string

        :returns: URI object
        :rtype: amigrations.adapters.uri.URI
        """
        return URI(self.db_uri)

    def transform_datetime_into_sql_format(self, datetime_val):
        """transforms datetime into format acceptable by a requested
        database. Most of them support datetime objects, but some not.
        For instance, sqlite doesn't accept datetime objects, instead it
        accepts timestamp

        :param datetime_val: datetime_object
        :type datetime_val: datetime.datetime
        :returns: applicable to asked database datetime format
        :rtype: datetime|int

        """
        return datetime_val.isoformat()

    def apply(self, name, migration, package):
        """Apply migration

        :param name: Migration name
        :type name: string
        :param migration: Sql to be applied
        :type migration: string
        :param package: package migration belongs to
        :type package: string
        :returns: None
        :rtype: None

        """
        cursor = self._client.cursor()
        with migration.open() as fp:
            cursor.execute(fp.read())
        name_splitted = name.split('_')
        applied_at = datetime.fromtimestamp(int(name_splitted[0]))
        applied_at = self.transform_datetime_into_sql_format(applied_at)
        cursor.execute("""
        INSERT INTO {} (name, applied_at, package)
        VALUES({placeholder}, {placeholder}, {placeholder})
        """.format(
            self.table_name, placeholder=self.placeholder
        ), [name, applied_at, package])
        print("\tApplied {}".format(name))

    def get_migrations_to_downgrade(self, downgrade_to_id):
        """Get migrations which are older than `downgrade_to_id`

        :param downgrade_to_id: Id of the migration database should be
        downgraded to, including this id
        :type downgrade_to_id: int
        :returns: A list of all migrations to be downgraded
        :rtype: [string, string, ...]

        """
        sql = (
            """SELECT name, id, package FROM {} WHERE id >= {placeholder}
             ORDER BY id DESC"""
            .format(
                self.table_name,
                placeholder=self.placeholder
            )
        )
        cursor = self._client.cursor()
        cursor.execute(sql, [downgrade_to_id, ])
        migrations = []
        for _row in cursor.fetchall():
            migrations.append(_row)
        return migrations

    def downgrade(self, migration_id, migration):
        """Downgrade migration by id and sql

        :param migration_id: migration id
        :type migration_id: int
        :param migration: sql to be downgraded
        :type migration: string
        :returns: None
        :rtype: None

        """

        cursor = self._client.cursor()
        with migration.open() as fp:
            cursor.execute(fp.read())
        cursor.execute("""
        DELETE FROM {} WHERE id = {placeholder}
        """.format(
            self.table_name, placeholder=self.placeholder
        ), [int(migration_id), ])
        print("\tDowngraded migration {}".format(migration.name))
