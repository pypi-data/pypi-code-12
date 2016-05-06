import os
from .template import Template


class TemplateWriter(object):

    def __init__(self, eureka_client, template_file, output_file):
        self._output_file = output_file
        self._template = Template(eureka_client, template_file)
        self.rendered = None

    def render(self):
        self.rendered = self._template.render()
        return self.rendered

    def write(self):
        if not os.path.exists(self._output_file) or \
           self.rendered != self.render():

            self._write_file(self.render())
            return True

        return False

    def _write_file(self, content):
        with open(self._output_file, 'w') as f:
            f.write(content)
