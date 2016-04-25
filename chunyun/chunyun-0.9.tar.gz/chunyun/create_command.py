import os

from .command import Command

CONFIG_TPL = """
[dev]
host = localhost
port = 5432
database = test
user = postgres
password =

[prod]
host = localhost
port = 5432
database = test
user = postgres
password =
"""


class CreateCommand(Command):

    def run(self):
        # 初始化config.ini文件
        config_path = os.path.join(self.args.dirname, 'config.ini')
        print("Creating config file {}".format(config_path))
        if os.path.exists(config_path):
            raise Exception("This folder has already initialized!")

        # 创建migrations目录
        migrations_path = os.path.join(self.args.dirname, "migrations")
        print("Creating directory {}".format(migrations_path))
        os.makedirs(migrations_path)

        with open(config_path, "w", encoding="utf-8") as handle:
            handle.write(CONFIG_TPL)

        print("The project is created successfully，pls config config.ini")
