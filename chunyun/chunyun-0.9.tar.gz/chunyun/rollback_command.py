import os
from configparser import ConfigParser
from tempfile import NamedTemporaryFile
import subprocess

from .command import Command

GET_LATEST_MIGRATION = '"SELECT name FROM chunyun_migrations ORDER BY ID DESC LIMIT 1"'
REMOVE_LATEST_MIGRATION = '''"DELETE FROM chunyun_migrations WHERE name = '{0}'"'''


class RollbackCommand(Command):

    def get_latest_migration(self, option):
        os.environ['PGPASSWORD'] = option.get(self.args.env, "password")
        cmd = "psql -h {host} -p {port}  -U {user} -t -c {sql} {name}".format(
                            host=option.get(self.args.env, 'host'),
                            port=option.get(self.args.env, 'port'),
                            user=option.get(self.args.env, 'user'),
                            name=option.get(self.args.env, 'database'),
                            sql=GET_LATEST_MIGRATION)
        handle = os.popen(cmd)
        output = handle.read().strip()
        handle.close()
        return output

    def remove_migration_record(self, option, name):
        os.environ['PGPASSWORD'] = option.get(self.args.env, "password")
        cmd = "psql -h {host} -p {port}  -U {user} -c {sql} {name}".format(
                            host=option.get(self.args.env, 'host'),
                            port=option.get(self.args.env, 'port'),
                            user=option.get(self.args.env, 'user'),
                            name=option.get(self.args.env, 'database'),
                            sql=REMOVE_LATEST_MIGRATION.format(name))
        handle = os.popen(cmd)
        output = handle.read()
        handle.close()

    def sync_migration(self, option, sql):
        handle = NamedTemporaryFile(delete=False)
        os.chmod(handle.name, 0o777)
        handle.write(sql.encode("utf-8"))
        handle.close()
        os.environ['PGPASSWORD'] = option.get(self.args.env, "password")
        cmd = 'psql -h {host} -p {port}  -U {user} -f "{file}" {name}'.format(
                            host=option.get(self.args.env, 'host'),
                            port=option.get(self.args.env, 'port'),
                            user=option.get(self.args.env, 'user'),
                            name=option.get(self.args.env, 'database'),
                            file=str(handle.name))
        cmd_handle = os.popen(cmd)
        output = cmd_handle.read()
        cmd_handle.close()
        os.unlink(handle.name)

    def run(self):
        parser = ConfigParser()
        parser.read("config.ini")

        # 获取migrations表里最新同步文件
        latest_migration = self.get_latest_migration(parser)

        if os.path.exists(os.path.join("migrations", latest_migration)):
            with open(os.path.join("migrations", latest_migration), encoding="utf-8") as handle:
                sql = handle.read()
                _, sql = sql.split("-- @down")
                self.sync_migration(parser, sql)
                print("rollback {}".format(latest_migration))
        else:
            print("{} does not exist".format(latest_migration))

        self.remove_migration_record(parser, latest_migration)
