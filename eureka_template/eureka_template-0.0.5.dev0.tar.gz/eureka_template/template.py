from .application import ApplicationCollection
from jinja2 import Environment, FileSystemLoader
import os


class Template(object):
    def __init__(self, eureka_client, template_file):
        self._eureka_client = eureka_client
        self._template_file = os.path.abspath(template_file)

    def _get_template(self):
        env = Environment(loader=FileSystemLoader('/'))
        return env.get_template(self._template_file)

    def _get_apps(self):
        apps_info = self._eureka_client.get_apps()["applications"]
        return ApplicationCollection.from_info(apps_info["application"])

    def render(self):
        return self._get_template().render(apps=self._get_apps())
