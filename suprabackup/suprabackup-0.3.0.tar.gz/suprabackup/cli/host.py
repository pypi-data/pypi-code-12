"""
This module contains host-related CLI commands

"""

from ..models import Host, Schedule


def create_host(session, logger, name, ip, schedule):
    """
    Creates an host with given parameters and schedule

    """
    sched = session.query(Schedule).filter(Schedule.name==schedule).one()
    host = Host(name=name, ip=ip, schedule=sched)
    session.add(host)
    logger.info("Created host {}".format(name))


def delete_host(session, logger, name):
    """
    Delete an host and its jobs from the database

    """
    host = session.query(Host).filter(Host.name==name).one()
    session.delete(host)
    logger.info("Deleted host {}".format(name))


def list_hosts(session, logger):
    """
    Lists all hosts in database

    """
    for host in session.query(Host).all():
        logger.info("- {}".format(host))
