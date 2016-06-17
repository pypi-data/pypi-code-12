"""
This module contains classes and helpers about backup schedule

"""

from sqlalchemy import Column
from sqlalchemy import Integer, String

from .base import Model


class Schedule(Model):
    """
    This is the ORM mapping for a schedule

    - short/long retentions are expressed in hours and define how much time we
    should keep the files
    - long_interval defines the interval of long-retention backups in hours

    Note that short_interval is not needed since this is the client which
    decides when to upload a backup, we just choose the type according to host
    jobs history.

    """
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    short_retention = Column(Integer)
    long_retention = Column(Integer)
    long_interval = Column(Integer)
