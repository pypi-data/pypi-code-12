import logging

from umodules.command import ICommand


class Install(ICommand):

    def run(self, project):
        logging.debug("- runnin [install] with {0}".format(project))

    def build(self, subparser):
        super().build(subparser)
        install = subparser.add_parser("install", help="Help")
        install.set_defaults(func=self.run)
        install.add_argument("modules", action="store", nargs="*")
        logging.debug("- [install] command has been added to argparse")

    def activate(self):
        super().activate()

