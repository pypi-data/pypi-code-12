import psycopg2

try:
    from stickshift.migration_repository import find_migration_index
except ImportError:
    from migration_repository import find_migration_index


def create_table_drop_query(table_name):
    return "DROP TABLE IF EXISTS {0} CASCADE;".format(table_name)


QUERY_LIST_FUNCTIONS = "SELECT routine_name " \
                       "FROM information_schema.routines " \
                       "WHERE routine_type='FUNCTION' " \
                       "AND specific_schema='public';"

QUERY_LIST_TABLES = "SELECT table_name " \
                    "FROM information_schema.tables " \
                    "WHERE table_schema = 'public';"

QUERY_CREATE_MIGRATION_TABLE = 'CREATE TABLE IF NOT EXISTS "version_migration" ' \
                               '(version INTEGER, migrated_at INTEGER DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP));'

QUERY_DROP_MIGRATION_TABLE = 'DROP TABLE IF EXISTS "version_migration";'

QUERY_DATABASE_MIGRATIONS_TABLE_EXISTS = "SELECT EXISTS (" \
                                         "SELECT 1 " \
                                         "FROM information_schema.tables " \
                                         "WHERE table_schema = 'public' AND table_name = 'version_migration'" \
                                         ");"
QUERY_DATABASE_CURRENT_VERSION = "SELECT MAX(version) FROM version_migration"

QUERY_DATABASE_INSERT_MIGRATION = "INSERT INTO version_migration(version) VALUES({0});"

QUERY_DATABASE_DELETE_MIGRATION = "DELETE FROM version_migration WHERE version = {0};"

QUERY_DATABASE_MIGRATION_VERSIONS = "SELECT * FROM version_migration;"

QUERY_RESET_DATABASE_MIGRATION_TABLE = create_table_drop_query("version_migration")


class DatabaseManager:

    def __init__(self, migration_repository, environment):
        self.migration_repository = migration_repository
        self.environment = environment
        self.database_config = migration_repository.database_config(self.environment)
        self.connection = None
        if self.database_config is not None:
            self.connection = psycopg2.connect(host=self.database_config["host"],
                                               port=self.database_config["port"],
                                               user=self.database_config["username"],
                                               password=self.database_config["password"],
                                               database=self.database_config["database"])
            self.connection.autocommit = True

    def provision_database(self):
        if self.is_database_provisioned():
            return False
        else :
            self.execute_create(QUERY_CREATE_MIGRATION_TABLE)
            return True

    def deprovision_database(self):
        if self.is_database_provisioned():
            self.execute_create(QUERY_DROP_MIGRATION_TABLE)
            return True
        else:
            return False

    def is_database_provisioned(self):
        result = self.execute_fetch(QUERY_DATABASE_MIGRATIONS_TABLE_EXISTS)
        return result[0]

    def current_database_migration_version(self):
        result = self.execute_fetch(QUERY_DATABASE_CURRENT_VERSION)
        return result[0]

    def list_migrations(self):
        return self.migration_repository.current_migrations_list()

    def list_procedures(self):
        return self.execute_fetch(QUERY_LIST_FUNCTIONS)

    def list_tables(self):
        return self.execute_fetch(QUERY_LIST_TABLES)

    def execute_create(self, query=None):
        if query is not None:
            with self.connection.cursor() as cursor:
                cursor.execute(query)

    def execute_fetch(self, query=None):
        if query is not None:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                results = [row[0] for row in cursor]
                return results

    def migrate(self):
        migration_list = self.migration_repository.current_migrations_list()
        current_migration_version = self.current_database_migration_version()
        if current_migration_version is not None:
            migration_list = migration_list[(current_migration_version+1):]
        for idx, migration_file_name in enumerate(migration_list):
            self.execute_migration(migration_file_name=migration_file_name,
                                   version_index=find_migration_index(migration_file_name))

    def upgrade(self):
        migration_list = self.migration_repository.current_migrations_list()
        current_migration_version = self.current_database_migration_version()
        if current_migration_version is not None:
            migration_list = migration_list[(current_migration_version+1):]
        next_migration = migration_list[0]
        self.execute_migration(migration_file_name=next_migration,
                               version_index=find_migration_index(migration_file_name=next_migration))

    def reset(self, limit=0):
        downgrade_list = self.migration_repository.current_downgrade_list()
        current_migration_version = self.current_database_migration_version()
        limit = current_migration_version
        if current_migration_version is not None:
            downgrade_list = downgrade_list[0:limit+1]
        else:
            return
        downgrade_list.reverse()
        for idx, migration_file_name in enumerate(downgrade_list):
            self.execute_downgrade(migration_file_name=migration_file_name,
                                   version_index=find_migration_index(migration_file_name))

    def downgrade(self):
        downgrade_list = self.migration_repository.current_downgrade_list()
        current_migration_version = self.current_database_migration_version()
        limit = current_migration_version
        if current_migration_version is not None:
            downgrade_list = downgrade_list[0:limit+1]
        else:
            return False
        downgrade_list.reverse()
        next_migration = downgrade_list[0]
        self.execute_downgrade(migration_file_name=next_migration,
                               version_index=find_migration_index(migration_file_name=next_migration))
        return True

    def execute_migration(self,
                          migration_file_name=None,
                          version_index=None):
        with self.connection.cursor() as cursor:
            cursor.execute(open(self.migration_repository.repository_upgrade_path() + "/" + migration_file_name, "r").read())
            cursor.execute(QUERY_DATABASE_INSERT_MIGRATION.format(version_index))
            print("Migration:{0} completed".format(migration_file_name))

    def execute_downgrade(self,
                          migration_file_name=None,
                          version_index=None):
        with self.connection.cursor() as cursor:
            cursor.execute(open(self.migration_repository.repository_downgrade_path() + "/" + migration_file_name, "r").read())
            cursor.execute(QUERY_DATABASE_DELETE_MIGRATION.format(version_index))
            print("Downgrade:{0} completed".format(migration_file_name))
