"""Contains the Queue class and the StopMode enumeration."""
import json
import logging
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from threading import Lock
from time import sleep

from bidon.db.access import transaction, pg_advisory_lock as adv
from bidon.util.date import utc_now

from .model import Job, SerializationKey
from .util import exception_to_message


LOGGER = logging.getLogger("pypgq")
CHANNEL_NAME = "pypgq_job_changed"


RunningJob = namedtuple("RunningJob", ["job", "sz_key", "future", "done"])
RunningJob.__new__.__defaults__ = (False, )


class StopMode(Enum):
  """Holds the states options for the queue."""
  never = 0x01
  when_all_done = 0x02
  when_current_done = 0x04
  now = 0x08


class Cooperative(object):
  """A class defining the cooperative modes for queues. All Queues running on
  a schema must be using the exact same cooperative mode.
  """
  none = 0x01
  advisory_lock = 0x02
  row_lock = 0x04

  def __init__(self, mode=None, args=None):
    """Initializes the cooperative instance

    :param mode: the cooperative mode. One of:
                 - Cooperative.none: the queue will not try to cooperate
                 - Cooperative.advisory_lock: the queue will cooperate via pg_advisory_lock
                 - Cooperative.row_lock: the queue will cooperative via
                                         `select for update skip locked`. Note this is only
                                         available in postgres 9.5+
    :param args: the additional args required by the mode.
                 - Cooperative.none: does not use args
                 - Cooperative.advisory_lock: either an integer, or a 2-tuple of integers, which is
                                              the key that the queue will use when obtaining
                                              advisory locks. Note that all queues operating on the
                                              same schema must all use the same advisory lock key
                 - Cooperative.row_lock: does not use args
    """
    self.mode = mode or self.none
    self.args = args


class Queue(object):
  """The job manager."""
  # pylint: disable=too-many-instance-attributes
  def __init__(self, model_access, worker_count=10, cooperative=None, schedule_frequency=60):
    """Initializes the Queue instance.

    :param model_access: a bidon.data.ModelAccess instance
    :param worker_count: the maximum number of workers to run at any one time
    :param cooperative: if True, the queue will pull workers using the Postgres
                        9.5+ feature `select for update skip locked` which will
                        enable multiple, cooperative queue processes.
    :param schedule_frequency: the time delay, in seconds, between calls to schedule_jobs. If None
                               this queue will not try to schedule jobs.
    """
    self._model_access = model_access
    self._worker_count = worker_count
    self._cooperative = cooperative
    self._schedule_frequency = schedule_frequency
    self._job_handlers = {}
    self._job_lock = Lock()
    self._executor = ThreadPoolExecutor(max_workers=worker_count)
    self._stop_mode = StopMode.never
    self._stop_callback = None
    self._waiting_job_count = 0
    self._running_jobs = {}
    self._completed_jobs = 0
    self._sleep_time = 0.1
    self._last_job_scheduling = None

  def add_handler(self, name, handler):
    """Registers a function to handle jobs with a given name.

    :param name: the job name to handle
    :param handler: the function to handle the job. This function should accept a
              single dict argument
    """
    if name in self._job_handlers:
      raise KeyError("A handler has already been registered for {}".format(name))
    self._job_handlers[name] = handler

  def start(self):
    """Starts the job handling loop."""
    self._loop()

  def stop(self, callback=None, stop_mode=StopMode.when_current_done):
    """Tell the job manager to stop.

    If the stop manner is less restrictive than the current stop manner, this
    function will do nothing.

    :param callback: assign a callback to be called when the manager stops
    :param stop_mode: an instance of the StopMode enum
    """
    if self._stop_mode.value < stop_mode.value:
      self._stop_callback = callback
      self._stop_mode = stop_mode
      LOGGER.info("Stop %s requested", stop_mode.name.replace("_", " "))

  def status(self):
    """Returns the current status of the JobQueue."""
    return dict(waiting_jobs=self._waiting_job_count,
                running_jobs=len(self._running_jobs),
                running_job_ids=tuple(sorted(self._running_jobs.keys())),
                completed_jobs=self._completed_jobs,
                stop_mode=self._stop_mode)

  def _loop(self):
    """The job handling loop. Runs until the state corresponding to
    self._stop_mode is matched.
    """
    LOGGER.info("Starting")

    # NOTE: There's a possible race condition here between when we start
    #       listening and when we get the waiting job count. If a job is added
    #       between starting to listen, and checking our count, the
    self._model_access.execute("listen {};".format(CHANNEL_NAME))

    self._waiting_job_count = self._model_access.count(Job.table_name, "started_at is null")
    self._running_jobs = {}

    while self._stop_mode != StopMode.now:
      sjcount = self._schedule_jobs()
      if sjcount is not None:
        LOGGER.info("Scheduled %s jobs", sjcount)

      self._update_job_list()

      # If the stop mode is never, or when all are done, continue to add jobs
      if self._stop_mode in (StopMode.never, StopMode.when_all_done):
        self._start_jobs()

      if not self._running_jobs:
        if self._stop_mode == StopMode.when_current_done:
          break
        if self._stop_mode == StopMode.when_all_done and self._waiting_job_count == 0:
          break

      sleep(self._sleep_time)

    # Cleanup any remaining futures. This will only happen when StopMode.now was requested.
    for (job_id, rjob) in self._running_jobs.items():
      rjob.future.cancel()
      self._model_access.update(Job.table_name,
                                dict(started_at=None,
                                     completed_at=None,
                                     error_message=None),
                                dict(id=job_id))
      if rjob.sz_key:
        self._model_access.update(SerializationKey.table_name,
                                  dict(active_job_id=None),
                                  dict(id=rjob.sz_key.id))
      LOGGER.info("Cancelled job %s", job_id)

    LOGGER.info("Stopping")

    self._model_access.close()

    if self._stop_callback:
      self._stop_callback()

  def _schedule_jobs(self):
    # Don't schedule jobs if the frequency is None
    if self._schedule_frequency is None:
      return None

    # Only perform a diff check if jobs have been scheduled
    if self._last_job_scheduling is not None:
      ts = utc_now().timestamp()

      # If the last scheduling timestamp plus the frequency is greater than the
      # current timestamp, it is not yet time to schedule.
      if self._last_job_scheduling + self._schedule_frequency > ts:
        return None

    with transaction(self._model_access):
      cr, _ = self._model_access.callproc("schedule_jobs", [])
      job_count = self._model_access.get_scalar(cr)

    self._last_job_scheduling = utc_now().timestamp()
    return job_count

  def _update_job_list(self):
    """Makes changes to the waiting job list and the running job list based on
    received notifications.
    """
    cn = self._model_access.connection

    # Gather any waiting notifications and update the job status info
    # accordingly
    cn.poll()

    for notify in cn.notifies:
      payload = json.loads(notify.payload)
      status = payload["status"]
      job_id = payload["job_id"]

      if status == "created":
        self._waiting_job_count += 1
      elif status == "started":
        if job_id not in self._running_jobs:
          self._waiting_job_count -= 1
      elif status == "completed":
        pass
      else:
        LOGGER.warning("Unknown job status %s for job %s", status, job_id)

    cn.notifies.clear()

    # Remove any completed jobs
    with self._job_lock:
      for job_id in [k for k, v in self._running_jobs.items() if v.done]:
        rjob = self._running_jobs[job_id]

        if rjob.done:
          self._finished_job(rjob.job, rjob.sz_key, rjob.future)
          self._running_jobs.pop(job_id)
          if rjob.job.error_message:
            LOGGER.info("Completed job %s with error", job_id, )
          else:
            LOGGER.info("Completed job %s", job_id, )
          self._completed_jobs += 1

  def _start_jobs(self):
    """Spawns as many new jobs as needed and possible."""
    available_workers = self._worker_count - len(self._running_jobs)
    start_new_count = min(self._waiting_job_count, available_workers)

    while start_new_count > 0:
      (job, sz_key, future) = self._start_a_job()

      if job:
        LOGGER.info("Started job %s", job.id)
        self._running_jobs[job.id] = RunningJob(job, sz_key, future, False)
        self._waiting_job_count -= 1
        start_new_count -= 1
        self._set_done_callback(future, job)
      else:
        start_new_count = 0

  def _start_a_job(self):
    """Either starts a waiting job and returns a 3-tuple of (job, sz_key, future),
    or finds no waiting job and returns a 3-tuple of (None, None, None).
    """
    with transaction(self._model_access):
      (job, sz_key) = self._get_next_job()

      if job is None:
        return (None, None, None)

      job.started_at = utc_now()
      if sz_key:
        sz_key.active_job_id = job.id

      self._update_job(job, sz_key)

    def fxn():
      """Future closure."""
      if job.name not in self._job_handlers:
        raise KeyError("Bad job name")
      self._job_handlers[job.name](job.payload)

    future = self._executor.submit(fxn)

    return (job, sz_key, future)

  def _get_next_job(self):
    """Returns a 2-tuple of (job, serialization_key) for the highest priority
    waiting job that has an open serialization key. Returns (None, None) if
    no such job exists.
    """
    if not self._cooperative:
      return self._get_next_job_inner()
    else:
      if self._cooperative.mode == Cooperative.none:
        return self._get_next_job_inner()
      elif self._cooperative.mode == Cooperative.advisory_lock:
        adv.obtain_lock(self._model_access, self._cooperative.args, xact=True)
        return self._get_next_job_inner()
      elif self._cooperative.mode == Cooperative.row_lock:
        return self._get_next_job_inner(row_lock=True)

  def _get_next_job_inner(self, *, row_lock=False):
    """Returns a 2-tuple of (job, serialization_key) for the highest priority
    waiting job that has an open serialization key. Returns (None, None) if
    no such job exists.
    """
    sql_fmt = ("select j.* "
               "from {job_table_name} as j "
               "left join {szk_table_name} as k on j.serialization_key_id = k.id "
               "where j.started_at is null and k.active_job_id is null "
               "order by j.priority desc, j.created_at asc "
               "limit 1")

    if row_lock:
      sql_fmt += " for update skip locked"

    job_data = self._model_access.execute(
      sql_fmt.format(
        job_table_name=Job.table_name,
        szk_table_name=SerializationKey.table_name)).fetchone()

    if job_data is None:
      return (None, None)

    job = Job(job_data)
    if job.serialization_key_id:
      sz_key = self._model_access.find_model_by_id(SerializationKey, job.serialization_key_id)
    else:
      sz_key = None

    return (job, sz_key)

  def _set_done_callback(self, future, job):
    """Sets the done_callback for the future and job. It is necessary to do this
    in a funciton here, rather than in a lambda in the loop, because the value
    of `job` changes during the loop.


    :param future: the future instance that is running the job
    :param job: the job model that is being run by the future
    """
    future.add_done_callback(lambda _: self._mark_job_done(job.id))

  def _update_job(self, job, sz_key):
    """Updates a job, and if present, its serialization key."""
    self._model_access.update_model(job,
                                    include_keys={"started_at", "completed_at", "error_message"})
    if sz_key:
      self._model_access.update_model(sz_key, include_keys={"active_job_id"})

  def _mark_job_done(self, job_id):
    """Marks the job with id :job_id: done."""
    with self._job_lock:
      rjob = self._running_jobs[job_id]
      self._running_jobs[job_id] = RunningJob(rjob.job, rjob.sz_key, rjob.future, True)

  def _finished_job(self, job, sz_key, future):
    """Marks the job as complete.

    :param job: the Job instance
    :param sz_key: the SerializationKey instance
    :param future: the Future instance that handled the job
    """
    error_message = exception_to_message(future.exception())
    job.update(completed_at=utc_now(), error_message=error_message)
    if sz_key:
      sz_key.active_job_id = None

    with transaction(self._model_access):
      self._update_job(job, sz_key)
