import logging

from command import ICommand


class Install(ICommand):

    def run(self, project):
        logging.debug("- installing with {0}".format(project))

    def build(self, subparser):
        install = subparser.add_parser("install", help="Help")
        install.set_defaults(func=self.run)
        install.add_argument("modules", action="store", nargs="*")

    def activate(self):
        super().activate()
        logging.debug("- install command has been activated")

