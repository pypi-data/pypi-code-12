"""
Contains database task utilities for CLI

"""

from ..db import Model
from ..models import Job, JobStatus

def purge_database(session, logger, older_than=0):
    """
    Purge cleaned-up backup jobs from database
    The older_than parameter will filter to purge only jobs older than the given
    number of hours

    """
    import datetime

    now = datetime.datetime.now()
    max_date = now - datetime.timedelta(hours=int(older_than))
    jobs = session.query(Job).filter(Job.status == JobStatus.PURGED, Job.end_time < max_date)
    count = jobs.count()
    for job in jobs.all():
        session.delete(job)
        logger.debug("Job {} purged from database".format(job.id))
    logger.info("Database purged: {} jobs removed".format(count))


def create_tables(session, logger):
    """
    Create the table needed for suprabackup in database
    Should be run once only

    """
    Model.metadata.create_all(session.get_bind())
    logger.info("Tables created in database")
