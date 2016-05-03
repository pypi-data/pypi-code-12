import yaml
import sys
from xdg import BaseDirectory


class Config:
    def __init__(self):
        try:
            file = open(BaseDirectory.xdg_config_home + '/infinityctl/config.yml', 'r')
        except FileNotFoundError:
            print("Файл конфигурации не найден")
            sys.exit(1)
        self.config = yaml.load(file)
        self.builds = self.config.get('builds')
        self.basedir = self.config.get('basedir')
        self.port = self.config.get('port')
        file.close()

    def get_build(self, name):
        try:
            return next((item for item in self.builds if item["name"] == name))
        except StopIteration:
            print('Указанный билд не найден')
            sys.exit(1)

