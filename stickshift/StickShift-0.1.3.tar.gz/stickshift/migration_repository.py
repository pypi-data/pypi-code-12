import os
import sys
import shutil
import natsort

python_version = sys.version_info.major
if python_version == 3:
    from configparser import ConfigParser, NoOptionError, NoSectionError
else:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError

DB_DIR = "db"
DB_CONFIG_PATH = "db/database.ini"
DB_CONFIG_FILE_CONTENTS = "[DATABASE]" \
                          "\nhost: [DB_HOST]" \
                          "\nport: [DB_PORT]" \
                          "\nusername: [DB_USERNAME]" \
                          "\npassword: [DB_PASSWORD]" \
                          "\ndatabase: [DB_NAME]\n"
DB_UPGRADE_DIR = "db/upgrade"
DB_DOWNGRADE_DIR = "db/downgrade"

DB_MAP_OPTIONS = ["host", "port", "username", "password", "database"]


def find_migration_index(migration_file_name):
    underscore_index = migration_file_name.index("_")
    return migration_file_name[1:underscore_index]


def parse_environment_variable(text):
    import re
    matches = re.findall(r'\[(.*?)\]', text)
    return matches


class InvalidEnvironmentError(Exception):
    pass


class InvalidDatabaseFieldError(Exception):
    pass


class MigrationRepository(object):

    def __init__(self, directory=None):
        self.directory = directory

    def repository_path(self):
        return self.path_for_directory_at_root_directory(path=DB_DIR)

    def repository_upgrade_path(self):
        return self.path_for_directory_at_root_directory(path=DB_UPGRADE_DIR)

    def repository_downgrade_path(self):
        return self.path_for_directory_at_root_directory(path=DB_DOWNGRADE_DIR)

    def repository_database_config_path(self):
        return self.path_for_directory_at_root_directory(path=DB_CONFIG_PATH)

    def path_for_directory_at_root_directory(self, path):
        if self.directory:
            path = '/'.join([self.directory, path])
        return path

    def is_repository_setup(self):
        return os.path.exists(self.repository_path())

    def clear(self):
        if self.is_repository_setup():
            shutil.rmtree(self.repository_path())
            return True
        else:
            return False

    def create_repository(self):
        if not self.is_repository_setup():
            os.mkdir(self.repository_path())
            os.mkdir(self.repository_upgrade_path())
            os.mkdir(self.repository_downgrade_path())

            with open(self.repository_database_config_path(), 'a') as config_file:
                config_file.write(DB_CONFIG_FILE_CONTENTS)

            return True
        else:
            return False

    def database_config(self, environment=None, database_fields=DB_MAP_OPTIONS):
        if environment is None:
            return None

        config = ConfigParser()
        config.read(self.repository_database_config_path())

        dict_map = {}
        for option in database_fields:
            try:
                config_value = config.get(environment, option)
                environment_values = parse_environment_variable(config_value)
                if len(environment_values) > 0:
                    config_value = os.environ.get(environment_values[0], "")
                dict_map[option] = config_value
            except NoSectionError:
                raise InvalidEnvironmentError("{0} is not a validly declared environment".format(environment))
            except NoOptionError:
                raise InvalidDatabaseFieldError("{0} is not a valid database field. \n"
                                                "Either add it to the database.ini file or see if its a valid field.".format(option))
        return dict_map

    def current_migration_count(self):
        return len(self.current_migrations_list())

    def current_downgrade_count(self):
        return len(self.current_downgrade_list())

    def current_migrations_list(self):
        return natsort.natsorted(os.listdir(self.repository_upgrade_path()))

    def current_downgrade_list(self):
        return natsort.natsorted(os.listdir(self.repository_downgrade_path()))

    def create_new_table_migration(self, name=None):
        if name:
            migration_count = self.current_migration_count()
            self.create_migration(name="create_table_{0}".format(name),
                                  directory=self.repository_upgrade_path(),
                                  contents="CREATE TABLE IF NOT EXISTS {0} ()".format(name),
                                  migration_index=migration_count)
            self.create_migration(name="drop_table_{0}".format(name),
                                  directory=self.repository_downgrade_path(),
                                  contents="DROP TABLE IF EXISTS {0} CASCADE;".format(name),
                                  migration_index=migration_count)

    def create_new_table_alteration_migration(self, name=None):
        if name:
            migration_count = self.current_migration_count()
            self.create_migration(name="alter_table_{0}".format(name),
                                  directory=self.repository_upgrade_path(),
                                  contents="/* Insert Table Alter statements here*/",
                                  migration_index=migration_count)
            self.create_migration(name="undo_alter_table_{0}".format(name),
                                  directory=self.repository_downgrade_path(),
                                  contents="/* Insert Table Alter statements here*/",
                                  migration_index=migration_count)

    def create_new_procedure_migration(self, name=None):
        if name:
            migration_count = self.current_migration_count()
            self.create_migration(name="create_sp_{0}".format(name),
                                  directory=self.repository_upgrade_path(),
                                  contents="CREATE OR REPLACE FUNCTION sp_{0} \n(\n\n) \n\nRETURNS RETURN_TYPE \n(\n) AS $$ "
                                           "\n\nBEGIN \n\nEND; $$ LANGUAGE plpgsql;".format(name),
                                  migration_index=migration_count)
            self.create_migration(name="drop_sp_{0}".format(name),
                                  directory=self.repository_downgrade_path(),
                                  contents="DROP FUNCTION IF EXISTS sp_{0};".format(name),
                                  migration_index=migration_count)

    def create_migration(self,
                         directory,
                         name,
                         contents,
                         migration_index=0):
        if migration_index < 10:
            migration_prefix = "V0{0}__".format(migration_index)
        else:
            migration_prefix = "V{0}__".format(migration_index)

        migration_file_name = migration_prefix + name + ".sql"
        migration_path = directory + "/" + migration_file_name
        print("Created migration:{0}".format(migration_path))
        migration_file = open(migration_path, 'a')
        if contents is not None:
            migration_file.write(contents)
        migration_file.close()
