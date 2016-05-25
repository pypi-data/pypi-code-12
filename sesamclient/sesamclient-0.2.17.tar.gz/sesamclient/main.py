# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import argparse
import configparser
import inspect
import json
import logging
import os.path
import pprint
import shutil
import sys
import textwrap

import appdirs
import requests.exceptions
import yaml

from . import Connection, PumpIsAlreadyRunning
from . import utils
from .exceptions import PipeAlreadyExists, SystemAlreadyExists

logger = logging.getLogger(__name__)


data_dir = appdirs.user_data_dir(appname="sesamclient", appauthor="Sesam")
configfilename = os.path.join(data_dir, "settings.ini")
myconfigparser = configparser.ConfigParser()
myconfigparser.read(configfilename, encoding="utf-8")


def print_message(message, file=None, indent=0):
    if message:
        if not message.endswith("\n"):
            message += "\n"
        if file is None:
            file = sys.stdout
        if indent:
            index_prefix = " " * indent
            message = textwrap.indent(message, index_prefix)
        file.write(message)
        file.flush()


def _exit(status=0, message=None):
    if message:
        print_message(message, sys.stderr)

    sys.exit(status)


def exit_with_error(message):
    _exit(status=1, message="error: " + message)


def config_cmd(args):
    """This function handles the 'config' command.

    Note that we don't have to check if the args.optionname is valid here, since that check has already been
    performed by the argparser.

    :param args: The arguments to the config-command.
    """
    logger.info("configcmd() running. args:%s" % (args,))

    if "." not in args.optionname:
        raise AssertionError("config key does not contain a section: %s" % (args.optionname,))

    section, optionname = args.optionname.split(".", maxsplit=1)

    if args.optionvalue:
        # set the config value
        optionvalue = " ".join(args.optionvalue)
        logger.info("configcmd: set the value of '%s.%s' to '%s'" % (section, optionname, optionvalue))
        if not myconfigparser.has_section(section):
            myconfigparser.add_section(section)
        myconfigparser.set(section, optionname, optionvalue)

        os.makedirs(data_dir, exist_ok=True)
        with open(configfilename, "w", encoding="utf-8") as configfile:
            myconfigparser.write(configfile)
    else:
        # get the configvalue
        value = myconfigparser.get(section, optionname, fallback="")
        if value:
            print(value)


def get_datasets_cmd(connection, args):
    # TODO: filtering
    datasets = connection.get_datasets()
    print_item_list(datasets, args)


def get_dataset_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)

    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))

    if args.out == "json":
        print_message(dataset.as_json())
    else:
        print_message(str(dataset))


def delete_dataset_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)
    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))
    dataset.delete()
    print_item(dataset, args)


def get_dataset_entities_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)

    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))

    # We must take care when printing out the entities, since it could be billions of them. We can't make a list and
    # print everything in one go, since that could take too much resources. Instead we get the raw byte-stream
    # from the server and copy it to sys.stdout.buffer. This is orders of magnitude faster than using the print_message()
    # function (or sys.stdout.write()) for each line.
    entities_stream = dataset.get_entities_as_stream(since=args.since, limit=args.limit, start=args.start,
                                                     history=args.history)
    shutil.copyfileobj(entities_stream, sys.stdout.buffer)
    sys.stdout.flush()


def get_dataset_entity_cmd(connection, args):
    dataset = connection.get_dataset(args.dataset_id)
    entity_id = args.entity_id

    if dataset is None:
        exit_with_error("No dataset with id '%s' was found!" % (args.dataset_id,))

    entity = dataset.get_entity(entity_id)
    print_item(entity, args)


def print_item_list(itemlist, args):

    if args.out == "json":
        if args.ids_only:
            json_object_list = [item.id for item in itemlist]
        else:
            json_object_list = [item.as_json_object() for item in itemlist]
        print_message(json.dumps(json_object_list, indent=4))

    elif args.out == "yaml":
        if args.ids_only:
            json_object_list = [item.id for item in itemlist]
        else:
            json_object_list = [item.as_json_object() for item in itemlist]

        print_message(yaml.dump(json_object_list))

    elif args.out == "plain":
        for item in itemlist:
            if args.ids_only:
                print_message(str(item.id))
            else:
                print_message(str(item))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def print_item(item, args):
    if isinstance(item, dict):
        json_object = item
    else:
        json_object = item.as_json_object()

    if args.out == "json":
        print_message(json.dumps(json_object, indent=4))

    elif args.out == "yaml":
        print_message(yaml.dump(json_object))

    elif args.out == "plain":
        print_message(str(item))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def get_pipes_cmd(connection, args):
    # TODO: filtering
    pipes = connection.get_pipes()
    print_item_list(pipes, args)


def get_pipe_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    print_item(pipe, args)


def add_pipes_cmd(connection, args):
    try:
        pipes = connection.add_pipes(args.pipe_configurations)
        print_item_list(pipes, args)
    except PipeAlreadyExists as e:
        exit_with_error("One or more of the pipes already exist: %s" % (e,))


def modify_pipe_cmd(connection, args):
    pipe_config = args.pipe_configuration
    pipe_id = pipe_config.get("_id")
    if not pipe_id:
        exit_with_error("The pipe-configuration doesn't contain a '_id' attribute! pipe_config: \n%s" % (
            pprint.pformat(pipe_config),))

    pipe = connection.get_pipe(pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (pipe_id,))

    pipe.modify(pipe_config)
    print_item(pipe, args)


def delete_pipe_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    pipe.delete()
    print_item(pipe, args)


def get_logs_cmd(connection, args):
    # TODO: filtering
    logs = connection.get_logs()
    print_item_list(logs, args)


def get_log_content_cmd(connection, args):
    log_content = connection.get_log_content(args.log_id)
    if log_content is None:
        exit_with_error("No log with id '%s' was found!" % (args.log_id,))
    shutil.copyfileobj(log_content, sys.stdout.buffer)
    sys.stdout.flush()


def get_systems_cmd(connection, args):
    # TODO: filtering
    systems = connection.get_systems()
    print_item_list(systems, args)


def get_system_cmd(connection, args):
    system = connection.get_system(args.system_id)
    if system is None:
        exit_with_error("No system with id '%s' was found!" % (args.system_id,))
    print_item(system, args)


def add_systems_cmd(connection, args):
    try:
        systems = connection.add_systems(args.system_configurations)
        print_item_list(systems, args)
    except SystemAlreadyExists as e:
        exit_with_error("One or more of the systems already exist: %s" % (e,))


def modify_system_cmd(connection, args):
    system_config = args.system_configuration
    system_id = system_config.get("_id")
    if not system_id:
        exit_with_error("The system-configuration doesn't contain a '_id' attribute! system_config: \n%s" % (
            pprint.pformat(system_config),))

    system = connection.get_system(system_id)
    if system is None:
        exit_with_error("No system with id '%s' was found!" % (system_id,))

    system.modify(system_config)
    print_item(system, args)


def delete_system_cmd(connection, args):
    system = connection.get_system(args.system_id)
    if system is None:
        exit_with_error("No system with id '%s' was found!" % (args.system_id,))
    system.delete()
    print_item(system, args)


def get_pump_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    pump = pipe.get_pump()
    print_item(pump, args)


def start_pump_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()
    try:
        pump.start(dont_wait_for_pump_to_start=args.dont_wait_for_pump_to_start)
    except PumpIsAlreadyRunning:
        if not args.allow_already_running_pump:
            exit_with_error("The pump of the pipe id '%s' is already running!" % (args.pipe_id,))

    if args.wait_timeout > 0:
        pump.wait_for_pump_to_finish_running(timeout=args.wait_timeout)

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Started the pump in this pipe:")
        print_message(str(pipe))
        print_message("=>", indent=2)
        print_message(str(pump), indent=4)

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def stop_pump_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()

    pump.stop()

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Stopped this  pump:")
        print_message(str(pump))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def disable_pump_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()
    pump.disable()

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Disabled this pump:")
        print_message(str(pump))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def enable_pump_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()
    pump.enable()
    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Enabled this pipe:")
        print_message(str(pipe))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def wait_for_pump_to_finish_running_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    pump = pipe.get_pump()
    pump.wait_for_pump_to_finish_running(timeout=args.timeout)

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Waited for this pipe:")
        print_message(str(pipe))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def unset_last_seen_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()
    pump.unset_last_seen()
    if args.out in ("json", "yaml"):
        print_item(pump, args)
    elif args.out == "plain":
        print_message("Updated this pump:")
        print_message(str(pump))
    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def update_last_seen_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()
    pump.update_last_seen(args.last_seen)
    if args.out in ("json", "yaml"):
        print_message(pump.as_json())
    elif args.out == "plain":
        print_message("Updated this pump:")
        print_message(str(pump))
    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def run_pump_operation_cmd(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))

    pump = pipe.get_pump()
    operation_parameters_list = args.operation_parameters
    operation_parameters = {}

    def strip_and_remove_enclosing_quotes(value):
        value = value.strip()
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            value = value.strip()
        return value

    if operation_parameters_list:
        for operation_parameter in operation_parameters_list:
            parameter_name, parameter_value = operation_parameter.split("=", 1)
            parameter_name = strip_and_remove_enclosing_quotes(parameter_name)
            parameter_value = strip_and_remove_enclosing_quotes(parameter_value)
            operation_parameters[parameter_name] = parameter_value

    pump.run_operation(args.operation, operation_parameters)
    if args.out in ("json", "yaml"):
        print_message(pump.as_json())
    elif args.out == "plain":
        print_message("Updated this pump:")
        print_message(str(pump))
    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def get_parser_used_by_sphinx_argparse_extension():
    """This is the method that is used when autogeneration documentation with the sphinx argparse extension.
    It has a quirk (or bug?) that causes it to print an "Undocumented" message  for subparsers that doens't have
    a "help"-parameter, even for subparsers that has a "description"-parameter. The "description"-parameter is the one
    that is actually displayed on the command line, so that is the one we want to use. But to get the sphinx-stuff to
    work we must specify the "help"-param instead of the "description"-param when we generate the parser the
    sphinx-stuff sees.
    """
    return get_parser(use_help_instead_of_description_for_subparsers=True)


def get_parser(use_help_instead_of_description_for_subparsers=False):
    description = """
description:
    This is a command line tool for connecting to a Sesam installation and performing
    various operations.

    The root address of the Sesam installation rest api can be specified with the --"server_base_url"
    argument, or by by using the 'config' command to store the address persistently.

    To get detailed help for a command, add '-h' after the command, like this:
      %%(prog)s config -h

    (version: %s)
    """ % (utils.get_version(),)

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--loglevel",
        help="The loglevel to use. The default is 'WARNING'",
        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='WARNING')

    # We use a separate subparser for each command. Each subparser gets assigned a function that gets called
    # when the user specifies the command in the command line arguments. This main() function does all the common
    # setup, while the subparser-functions does all the command-specific stuff.
    subparsers = parser.add_subparsers()

    # noinspection PyShadowingBuiltins
    def add_subparser(*args,
                      add_default_arguments=True,
                      add_default_arguments_for_list_commands=False,
                      help=None, description=None,
                      **kwargs):
        subparser_kwargs = dict(**kwargs)
        subparser_kwargs["help"] = help
        subparser_kwargs["description"] = description
        if use_help_instead_of_description_for_subparsers and (help is None):
            subparser_kwargs["help"] = description
            subparser_kwargs["description"] = None
        subparser = subparsers.add_parser(*args, **subparser_kwargs)

        if add_default_arguments:

            subparser.add_argument(
                "--server_base_url",
                metavar="<server base url>",
                help="""The server base url to use. If specified, this overrides any default value that has been set with the
                        'config' command. Example usage: --server_base_url http://localhost:10001/api""")

            subparser.add_argument(
                "--server_username",
                metavar="<username>",
                help="""The username to use when authenticating to the server. If specified, this overrides any default value
                        that has been set with the
                        'config' command. Example usage: --server_username olanorman""")

            subparser.add_argument(
                "--server_password",
                metavar="<password>",
                help="""The password to use when authenticating to the server. If specified, this overrides any default value
                        that has been set with the
                        'config' command. Example usage: --server_password verysecret""")

            subparser.add_argument(
                "--server_timeout",
                metavar="<timeout in seconds>",
                help="""The server timeout to use. If specified, this overrides any default value that has been set with the
                        'config' command. Example usage: --server_timeout 60""")

            subparser.add_argument(
                "--out",
                choices=['json', 'yaml', 'plain'],
                default='json',
                help="""The output format to use. The default format is 'json'.""")

        if add_default_arguments_for_list_commands:
            subparser.add_argument(
                "--ids-only",
                default=False,
                action='store_true',
                help="""If this is specified, only the id's of the items will be displayed.""")

        return subparser
        
    # The "config"-command is used to set or get persistently stored configuration options (server root url, etc).
    configcmd_parser = add_subparser(
        "config",
        description="Gets or sets a config option.",
        add_default_arguments=False  # The config sub-command is special, and doesn't use the default args.
    )
    configcmd_parser.add_argument(
        "optionname", help="The config option to get or set",
        choices=["server.base_url",
                 "server.username",
                 "server.password",
                 "server.timeout",
                 ])
    configcmd_parser.add_argument(
        "optionvalue",
        help="If specified, the config option will be set to this value. "
             "If no value is specified, the current value will be displayed.",
        nargs=argparse.REMAINDER,
        default=None)
    configcmd_parser.set_defaults(subparser_func=config_cmd)

    get_pipes_parser = add_subparser(
        "get-pipes",
        description="Display a list of pipes",
        add_default_arguments_for_list_commands=True)
    get_pipes_parser.set_defaults(subparser_func=get_pipes_cmd)

    get_pipe_parser = add_subparser(
        "get-pipe",
        description="Display detailed information about the specified pipe")
    get_pipe_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    get_pipe_parser.set_defaults(subparser_func=get_pipe_cmd)

    add_pipes_parser = add_subparser(
        "add-pipes",
        description="Add one or more new pipes",
        add_default_arguments_for_list_commands=True
    )
    add_pipes_parser.add_argument(
        "pipe_configurations",
        type=json.loads,
        help="A list of the configurations of the new pipes. Each pipe configuration should be a json-encoded dict on "
             "the same format as used when  defining a pipe in the sesam-node configuration file. "
             """Example: '[{"_id": "my_new_pipe", "type": "pipe", "short_config": "sql://Northwind/Customers"}]'
             """)
    add_pipes_parser.set_defaults(subparser_func=add_pipes_cmd)

    modify_pipe_parser = add_subparser(
        "modify-pipe",
        description="Modify a pipe by uploading a new configuration for the pipe")
    modify_pipe_parser.add_argument(
        "pipe_configuration",
        type=json.loads,
        help="The new configuration of the pipe. This should be a json object on the same format as used when "
             "defining a pipe in the sesam-node configuration file. The pipe to modify is specified by the '_id' "
             "attribute of the configuration. "
             """Example: '{"_id": "my_existing_pipe", "type": "pipe", "short_config": "sql://Northwind/Customers"}'"
             """)
    modify_pipe_parser.set_defaults(subparser_func=modify_pipe_cmd)

    delete_pipe_parser = add_subparser(
        "delete-pipe",
        description="Deletes the specified pipe from the sesam-node")
    delete_pipe_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    delete_pipe_parser.set_defaults(subparser_func=delete_pipe_cmd)


    get_logs_parser = add_subparser(
        "get-logs",
        description="Display a list of logs",
        add_default_arguments_for_list_commands=True)
    get_logs_parser.set_defaults(subparser_func=get_logs_cmd)

    get_log_parser = add_subparser(
        "get-log",
        description="Display the content of the specified log")
    get_log_parser.add_argument(
        "log_id",
        help="The id of the log.")
    get_log_parser.set_defaults(subparser_func=get_log_content_cmd)

    get_systems_parser = add_subparser(
        "get-systems",
        description="Display a list of systems",
        add_default_arguments_for_list_commands=True)
    get_systems_parser.set_defaults(subparser_func=get_systems_cmd)

    get_system_parser = add_subparser(
        "get-system",
        description="Display detailed information about the specified system")
    get_system_parser.add_argument(
        "system_id",
        help="The id of the system.")
    get_system_parser.set_defaults(subparser_func=get_system_cmd)

    add_systems_parser = add_subparser(
        "add-systems",
        description="Add one or more new systems",
        add_default_arguments_for_list_commands=True
    )
    add_systems_parser.add_argument(
        "system_configurations",
        type=json.loads,
        help="A list of the configurations of the new systems. Each system configuration should be a json-encoded dict on "
             "the same format as used when  defining a system in the sesam-node configuration file. "
             """Example: '[{"_id": "my_new_system", "type": "system", "short_config": "sql://Northwind/Customers"}]'
             """)
    add_systems_parser.set_defaults(subparser_func=add_systems_cmd)

    modify_system_parser = add_subparser(
        "modify-system",
        description="Modify a system by uploading a new configuration for the system")
    modify_system_parser.add_argument(
        "system_configuration",
        type=json.loads,
        help="The new configuration of the system. This should be a json object on the same format as used when "
             "defining a system in the sesam-node configuration file. The system to modify is specified by the '_id' "
             "attribute of the configuration. "
             """Example: '{"_id": "my_existing_system", "type": "system", "short_config": "sql://Northwind/Customers"}'"
             """)
    modify_system_parser.set_defaults(subparser_func=modify_system_cmd)

    delete_system_parser = add_subparser(
        "delete-system",
        description="Deletes the specified system from the sesam-node")
    delete_system_parser.add_argument(
        "system_id",
        help="The id of the system.")
    delete_system_parser.set_defaults(subparser_func=delete_system_cmd)

    get_datasets_parser = add_subparser(
        "get-datasets",
        description="Display a list of datasets",
        add_default_arguments_for_list_commands=True)
    get_datasets_parser.set_defaults(subparser_func=get_datasets_cmd)

    get_dataset_parser = add_subparser(
        "get-dataset",
        description="Display detailed information about the specified dataset")
    get_dataset_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    get_dataset_parser.set_defaults(subparser_func=get_dataset_cmd)

    delete_dataset_parser = add_subparser(
        "delete-dataset",
        description="Deletes the specified dataset from the sesam-node")
    delete_dataset_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    delete_dataset_parser.set_defaults(subparser_func=delete_dataset_cmd)

    get_dataset_entities_parser = add_subparser(
        "get-dataset-entities",
        description="Returns the entities of the specified dataset")
    get_dataset_entities_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    get_dataset_entities_parser.add_argument(
        "--since",
        help="""The "since" parameter is the opaque value that can be used to efficiently skip already \
seen entities.""", default=None)
    get_dataset_entities_parser.add_argument(
        "--limit",
        help="""The "limit" parameter specifies the maximum number of entities to return. \
If this is not specified, all available entities are returned.""",
        default=None)
    get_dataset_entities_parser.add_argument(
        "--start",
        help="""The "start" parameter is a positive integer that specified how many entities to skip from the \
start of where the "since"-parameters starts. This is far less efficient than using the "since"-parameter, but it \
can be manually set in a gui to explore the dataset. NOTE: Clients should use the "since"-parameter whenever \
possible.""",
        default=0)
    get_dataset_entities_parser.add_argument(
        "--history",
        default=True,
        help="""If this is true (the default) all entities, including replaced ones, will be returned. \
If this is false, only the latest version of the entities will be returned""")
    get_dataset_entities_parser.set_defaults(subparser_func=get_dataset_entities_cmd)

    get_dataset_entity_parser = add_subparser(
        "get-dataset-entity",
        description="Returns the specified entity of the specified dataset")
    get_dataset_entity_parser.add_argument(
        "dataset_id",
        help="The id of the dataset.")
    get_dataset_entity_parser.add_argument(
        "entity_id",
        help="The id of the entity.")
    get_dataset_entity_parser.set_defaults(subparser_func=get_dataset_entity_cmd)

    get_pump_parser = add_subparser(
        "get-pump",
        description="Display detailed information about the pump in the specified pipe")
    get_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    get_pump_parser.set_defaults(subparser_func=get_pump_cmd)

    stop_pump_parser = add_subparser(
        "stop-pump",
        description="Stop the pump in the specified pipe")
    stop_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    stop_pump_parser.set_defaults(subparser_func=stop_pump_cmd)

    start_pump_parser = add_subparser(
        "start-pump",
        description="Run the pump in the speficied pipe")
    start_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    start_pump_parser.add_argument(
        "--allow-already-running-pump",
        default=False,
        action='store_true',
        help="This option will make the command ignore an already running pump. Normally, that is treated as an error.")
    start_pump_parser.add_argument(
        "--dont-wait-for-pump-to-start",
        default=False,
        action='store_true',
        help="This option will prevent the command from waiting for the pump to start before returning. This is useful "
             "for batch-operations where you want to schedule lots of pumps to run, but don't wait for the server to "
             "actually start them all.")
    start_pump_parser.add_argument(
        "--wait-timeout",
        dest="wait_timeout",
        default=0,
        type=int,
        help="If this is not zero (the default), the command will wait for the pump to finish running. "
             "If the pump hasn't stopped within the specified number of seconds, an error is raised.")
    start_pump_parser.set_defaults(subparser_func=start_pump_cmd)

    disable_pump_parser = add_subparser(
        "disable-pump",
        description="Disable the pump in the specified pipe")
    disable_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    disable_pump_parser.set_defaults(subparser_func=disable_pump_cmd)

    enable_pump_parser = add_subparser(
        "enable-pump",
        description="Enable the pump in the specified pipe")
    enable_pump_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    enable_pump_parser.set_defaults(subparser_func=enable_pump_cmd)
    
    wait_for_pump_to_finish_running_parser = add_subparser(
        "wait-for-pump-to-finish-running",
        description="Wait for the pump in the specified pipe to finish running")
    wait_for_pump_to_finish_running_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    wait_for_pump_to_finish_running_parser.add_argument(
        "timeout",
        default=60,
        type=int,
        help="The maximum number of seconds to wait.")
    wait_for_pump_to_finish_running_parser.set_defaults(subparser_func=wait_for_pump_to_finish_running_cmd)

    unset_last_seen_parser = add_subparser(
        "unset-last-seen",
        description="Unset 'last seen' token on the specified pipe")
    unset_last_seen_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    unset_last_seen_parser.set_defaults(subparser_func=unset_last_seen_cmd)

    update_last_seen_parser = add_subparser(
        "update-last-seen",
        description="Update the 'last seen' token on the specified pipe")
    update_last_seen_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    update_last_seen_parser.add_argument(
        "last_seen",
        help="The new last change token. For sdshare-clients, this should be on the form: '2015-07-20T10:00:15Z'")
    update_last_seen_parser.set_defaults(subparser_func=update_last_seen_cmd)

    run_pump_operation_parser = add_subparser(
        "run-pump-operation",
        description="""This is a special generic command that runs the specified operation on the specified pipe.
The usecase is pipes that support operations that aren't part of the 'official'sesam-api, and operations that hasn't
yet gotten their own dedicated command in the command-line client.""")
    run_pump_operation_parser.add_argument(
        "pipe_id",
        help="The id of the pipe.")
    run_pump_operation_parser.add_argument(
        "operation",
        help="The operation to run.")
    run_pump_operation_parser.add_argument(
        "-d",
        action="append",
        metavar="<parametername>=<parametervalue>",
        dest="operation_parameters",
        help="""A <parametername>=<parametervalue> pair. This option can be specified zero or more times. Example: -d last-seen="2015-07-20T10:00:15Z".""")
    run_pump_operation_parser.set_defaults(subparser_func=run_pump_operation_cmd)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    loglevel = {
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG}[args.loglevel]

    logging.basicConfig(level=loglevel,
                        format="%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s")

    logger.info("main() running")
    logger.info("Using config file '%s'" % (configfilename,))

    sesamapi_base_url = myconfigparser.get("server",
                                           "base_url",
                                           fallback=getattr(args, "server_base_url", ""))

    logger.info("sesamapi_base_url: '%s'" % (sesamapi_base_url,))

    if hasattr(args, "subparser_func"):
        # A command was specified

        # check if the subparser_func wants a Connection parameter.
        argspec = inspect.getfullargspec(args.subparser_func)
        if argspec.args[0] == "connection":
            # Ok, this function wants a connection argument
            sesamapi_base_url = getattr(args, "server_base_url")
            if not sesamapi_base_url:
                sesamapi_base_url = myconfigparser.get("server", "base_url", fallback="")
            if not sesamapi_base_url:
                exit_with_error(
                    "No server base_url specified! Either use the 'config server.base_url <baseurl>'-command to specify a default base_url, "
                    "or specify the base_url with the '--server_base_url' parameter.")

            username = getattr(args, "server_username", myconfigparser.get("server", "username", fallback=""))
            password = getattr(args, "server_password", myconfigparser.get("server", "password", fallback=""))
            timeout = int(myconfigparser.get("server", "timeout", fallback="") or 30)
            connection = Connection(sesamapi_base_url=sesamapi_base_url,
                                    username=username,
                                    password=password,
                                    timeout=timeout,
                                    )
            try:
                args.subparser_func(connection, args)
            except requests.exceptions.ConnectionError as e:
                exit_with_error(
                    "Failed to connect to the sesam installation at '%s'! The following error occurred: %s" % (
                        sesamapi_base_url, e))

        else:
            # This function does not want a connection argument
            args.subparser_func(args)

    else:
        # no command was specified
        parser.print_usage()

if __name__ == "__main__":
    main()
