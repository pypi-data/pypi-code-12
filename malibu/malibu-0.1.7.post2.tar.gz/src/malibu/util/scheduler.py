# -*- coding: utf-8 -*-
import abc
import pkg_resources
from datetime import datetime, timedelta

from malibu.config import configuration
from malibu.design import borgish
from malibu.util.decorators import function_registrator

__JOB_STORES__ = []
job_store = function_registrator(__JOB_STORES__)
__LOADED_EXTERNAL_JS__ = False


def _load_external_jobstores():

    # Load job stores marked with the malibu.scheduler.job_stores entry point
    for st in pkg_resources.iter_entry_points('malibu.scheduler.job_stores'):
        # Since the job stores are registered automatically with the @job_store
        # decorator, we simply have to do a load and we're done.
        st.load()


class Scheduler(borgish.SharedState):

    def __init__(self, store='volatile', *args, **kw):

        super(Scheduler, self).__init__(*args, **kw)

        global __LOADED_EXTERNAL_JS__
        if not __LOADED_EXTERNAL_JS__:
            _load_external_jobstores()
            __LOADED_EXTERNAL_JS__ = True

        self._config = None
        self._jsconfig = None

        # Load the Scheduler configuration if it was provided.
        if "config" in kw:
            c = kw.get("config", None)
            if c and c.has_section("scheduler"):
                self._config = c.get_section("scheduler")

            # Check for the job store configuration
            if self._config and self._config.get("job_store", None):
                jsc = self._config.get("job_store")
                # The type of job store set in the config should override
                # the `store` param, always.
                if jsc:
                    # Set the job store config immutable.
                    jsc.set_mutable(False)
                    # Store the job store config and store type
                    self._jsconfig = jsc
                    store = jsc.get_string("type", "volatile")

        # Make sure the job store doesn't get reinitialized after loading
        # state through the SharedState mixin.
        if "state" not in kw:
            job_store = list(filter(lambda s: s.TYPE == store, __JOB_STORES__))
            if not job_store or len(job_store) == 0:
                raise SchedulerException(
                    "Could not find a job store for type: %s" % (store))
            elif len(job_store) > 1:
                raise SchedulerException(
                    "Selected more than one job store for type: %s" % (store))

            kwa = {
                "config": self._jsconfig,
            }

            job_store = job_store[0]
            self._job_store = job_store(self, **kwa)

    @property
    def job_store(self):

        return self._job_store

    def create_job(self, name, func, delta, recurring=False):
        """ Creates a new job instance and attaches it to the scheduler.

            Params
            ------
            name : str
                Name of the job to create.
            func : function
                Function that is specified as the execution callback.
            delta : datetime.timedelta
                Timedelta to execute on.
            recurring : bool, optional
                Whether the job should continue running after first run.

            Raises
            ------
            SchedulerException
                If the job already exists, func is none, or delta is not
                an instance of datetime.timedelta.

            Returns
            -------
            SchedulerJob
                If job creation was succesful.
        """

        if self.job_store.get_job(name):
            raise SchedulerException("Job already exists; remove it first.")
        if func is None:
            raise SchedulerException("Callback function is non-existent.")
        if not isinstance(delta, timedelta):
            raise SchedulerException(
                "Argument 'delta' was not a timedelta instance.")

        job = SchedulerJob(name, func, delta, recurring)
        self.add_job(job)

        return job

    def add_job(self, job):
        """ Adds a job to the list of jobs maintained by the scheduler.

            Params
            ------
            job : SchedulerJob
                Job to add to the list of active jobs.

            Raises
            ------
            SchedulerException
                If the job already exists in the jobs dictionary.
        """

        if self.job_store.get_job(job.get_name()):
            raise SchedulerException("Job already exists; remove it first.")

        job.begin_ticking()
        self.job_store.store(job)

    def remove_job(self, name):
        """ Removes a job from the list of jobs maintained by the scheduler.

            Params
            ------
            name : str
                Name of the job to remove from the job list.

            Raises
            ------
            SchedulerException
                If the job does not exist.
        """

        if not self.job_store.get_job(name):
            raise SchedulerException("Job does not exist.")

        self.job_store.destore(self.job_store.get_job(name))

    def tick(self):
        """ Gets the current time and checks the ETA on each job.
            If the job is ready, it executes and captures any exception
            that should raise out of the execute call.
            If an exception is captured, the job's onfail callbacks will be
            fired with a reference to the job object that was being triggered.
        """

        now = datetime.now()

        mark_removal = []

        for job in self.job_store.get_jobs():
            if job.is_ready(now):
                try:
                    job.execute()
                    job.set_traceback(None)
                except Exception as e:
                    job.set_traceback(e)
                    job.fire_onfail()

                mark_removal.append(job)

        for job in mark_removal:
            self.remove_job(job.get_name())
            if job.is_recurring():
                self.add_job(job)


class SchedulerJobStore(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, scheduler, *args, **kw):
        """ Initializes the job store.
        """

        self._scheduler = scheduler

        if "config" in kw:
            self.initialize(kw.get("config"))

    @abc.abstractmethod
    def initialize(self, config):
        """ Provides initialization from a Configuration object for job store
            implementations that need it.
        """

        if not isinstance(config, configuration.ConfigurationSection):
            raise TypeError("Expected instance of malibu.config."
                            "Configuration.ConfigurationSection, not %s" % (
                                config.__class__.__name__))

        return

    @staticmethod
    def updates_store(func):
        """ Decorator that forces an update of a job in the store after the
            decorated function is run.
        """

        def _funcarg_decorator(*args, **kw):
            """ This function chain will call the given function and then
                attempt to re-store the job in the job store.
            """

            func(*args, **kw)

            # Since we don't know the location of the job in the function
            # arguments, we can look in two places to sort-of enforce a
            # structure:
            #  - In the first *args slot
            #  - In the 'job' **kw slot.
            job = None
            if len(args) > 0:
                job = args[0]

            if not job or not isinstance(job, SchedulerJob):
                job = kw.get('job', None)

            if not job or not isinstance(job, SchedulerJob):
                # Best we can do here is just return or warn.
                return

            scheduler = job._scheduler
            store = scheduler.job_store
            store.store(job, update=True)

        return _funcarg_decorator

    @abc.abstractmethod
    def get_jobs(self):
        """ Returns all jobs in the job store.
        """

        return

    @abc.abstractmethod
    def get_job(self, job_name):
        """ Returns a job from the store with the given name.
        """

        return

    @abc.abstractmethod
    def store(self, job, update=False):
        """ Serializes a job into the job store.
        """

        if not isinstance(job, SchedulerJob):
            raise TypeError("Job argument is not an instance of SchedulerJob")

        return

    @abc.abstractmethod
    def destore(self, job):
        """ Removes a job from the job store.
        """

        if not isinstance(job, SchedulerJob):
            raise TypeError("Job argument is not an instance of SchedulerJob")

        return


@job_store
class VolatileSchedulerJobStore(SchedulerJobStore):
    """ Implements a purely in-memory job store backed by a dictionary.

        This job store type does not need a set of configurations pass in to
        it. Any jobs pushed into this store will be lost when the application
        is shut down!
    """

    TYPE = 'volatile'

    def __init__(self, scheduler, *args, **kw):

        super(VolatileSchedulerJobStore, self).__init__(scheduler)

        self.__jobs = {}

    def initialize(self, config):

        return

    def get_jobs(self):

        return self.__jobs.values()

    def get_job(self, job_name):

        return self.__jobs.get(job_name, None)

    def store(self, job, update=False):

        super(VolatileSchedulerJobStore, self).store(job, update)

        if job.get_name() in self.__jobs and not update:
            return False

        self.__jobs.update({job.get_name(): job})

        return True

    def destore(self, job):

        super(VolatileSchedulerJobStore, self).destore(job)

        if job.get_name() not in self.__jobs:
            return False

        return True if self.__jobs.pop(job.get_name()) else False


class SchedulerJob(object):

    def __init__(self, name, function, delta, state, recurring=False):

        self._scheduler = Scheduler()
        self._name = name
        self._function = function
        self._delta = delta
        self._recurring = recurring
        self._last_traceback = None
        self._onfail = []
        self._metadata = {}
        self.onfail = function_registrator(self._onfail)

        self._eta = delta

    @property
    def metadata(self):

        return self._metadata

    def get_name(self):

        return self._name

    def get_eta(self):

        return self._eta

    def get_traceback(self):

        return self._last_traceback

    @SchedulerJobStore.updates_store
    def set_traceback(self, stack):

        self._last_traceback = stack

    @SchedulerJobStore.updates_store
    def attach_onfail(self, func):

        self._onfail.append(func)

    @SchedulerJobStore.updates_store
    def detach_onfail(self, func):

        self._onfail.remove(func)

    def fire_onfail(self):

        for callback in self._onfail:
            callback(job=self)

    def is_recurring(self):

        return self._recurring

    def is_ready(self, time):

        if time >= self._eta:
            return True
        else:
            return False

    @SchedulerJobStore.updates_store
    def begin_ticking(self):

        self._eta = datetime.now() + self._delta

    @SchedulerJobStore.updates_store
    def execute(self):

        self._function()

        if self._recurring:
            self._eta += self._delta


class SchedulerException(Exception):

    def __init__(self, value):

        self.value = value

    def __str__(self):

        return repr(self.value)
