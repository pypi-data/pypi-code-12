"""
This module contains all host-related classes and helpers

"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, backref

from .base import Model
from .job import Job


class Host(Model):
    """
    This is the ORM mapping for the hosts table

    """
    IP_MAX_LENGTH = 45

    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    ip = Column(String(IP_MAX_LENGTH))
    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    schedule = relationship('Schedule', backref='hosts')
    jobs = relationship('Job', backref='host', lazy='dynamic')


    @property
    def last_long_job(self):
        """
        Get the last long job

        """
        jobs = self.jobs.filter(Job.type == Job.LONG).order_by(Job.end_time.desc())
        if jobs.count:
            return jobs.first()
        else:
            return None


    def new_job(self, start_time=None, path=''):
        """
        Create a job instance with correct parameters and return it

        """
        import datetime

        if not start_time:
            start_time = datetime.datetime.now()
        last_long = self.last_long_job
        job = Job(host=self, start_time=start_time, file_path=path)
        if not last_long:
            job.type = Job.LONG
        else:
            next_long = last_long.end_time
            next_long += datetime.timedelta(hours=self.schedule.long_interval)
            if start_time > next_long:
                job.type = Job.LONG
        return job
