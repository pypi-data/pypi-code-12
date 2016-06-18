import argparse


def cmd_install():
    print("Hello World")


def create_options(parser):

    parser.add_argument("-c", "--config", dest="config", help="use a different configuration file",
                        default="project.yml")

    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="show more information on console when running", default=None)


def create_commands(subparser, commands):

    for command in commands:
        command.plugin_object.build(subparser)


def create_parser(commands):

    parser = argparse.ArgumentParser(prog='uModules', description="uModules 0.3")
    subparser = parser.add_subparsers(dest="command")
    subparser.required = True

    create_options(parser)
    create_commands(subparser, commands)

    return parser
