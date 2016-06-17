"""
This packages contains CLI utils for suprabackup.
It provides tools to allow things such as hosts/schedules creation, etc

"""
import argparse

from ..models import *

from .host import create_host, delete_host, list_hosts
from .schedule import create_schedule, delete_schedule, list_schedules
from .db import purge_database, create_tables


__motd__ = """
###############################
### Welcome to Suprashell ! ###
###############################

Use quit() or ^D to Exit

Available resources are:
 - session: An handler to a SQLAlchemy session
 - config: A SupraConfig dictionary
 - Host: the host model
 - Job: the job model
 - JobStatus: the JobStatus enum
 - Schedule: the schedule model

"""

__cmds__ = {
    'create_host': create_host,
    'delete_host': delete_host,
    'list_hosts': list_hosts,
    'create_schedule': create_schedule,
    'delete_schedule': delete_schedule,
    'list_schedules': list_schedules,
    'purge_database': purge_database,
    'create_tables': create_tables,
}


def cli(session, logger, cmd, *args):
    """
    This wrapper calls the correct method in registered in __cmds__

    """
    c = __cmds__.get(cmd, None)
    if not c:
        logger.error("No such command {}".format(cmd))
        return
    return c(session, logger, *args)


def shell(session, config):
    """
    This function offers an interactive shell with few objects imported
    This is useful to quickly deal with the database

    """
    from code import InteractiveConsole

    vars = {
        'session': session,
        'config': config,
        'Host': Host,
        'Schedule': Schedule,
        'Job': Job,
        'JobStatus': JobStatus,
        }
    console = InteractiveConsole(vars)
    console.interact(banner=__motd__)
