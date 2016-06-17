"""
This module contains Schedule-related CLI commands

"""

from ..models import Schedule


def create_schedule(session, logger, name, short_retention, long_retention, long_interval):
    """
    Creates a schedule in database

    """
    sched = Schedule(name=name,
                     short_retention=short_retention,
                     long_retention=long_retention,
                     long_interval=long_interval)
    session.add(sched)
    logger.info("Created schedule {}".format(name))


def delete_schedule(session, logger, name):
    """
    Deletes a schedule from database

    """
    sched = session.query(Schedule).filter(name=name).one()
    session.delete(sched)
    logger.info("Deleted schedule {}".format(name))


def list_schedules(session, logger):
    """
    List schedules in database

    """
    for sched in session.query(Schedule).all():
        logger.info("- {}".format(sched))
