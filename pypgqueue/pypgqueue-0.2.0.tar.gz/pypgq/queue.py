"""Contains the Queue class and the StopMode enumeration."""
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
from enum import Enum
from threading import Lock
from time import sleep

from bidon.db.access import transaction
from bidon.util.date import utc_now

from .model import Job, SerializationKey
from .util import exception_to_message


LOGGER = logging.getLogger("pypgq")
SLEEP = 1.0
CHANNEL_NAME = "pypgq_job_changed"


RunningJob = namedtuple("RunningJob", ["job", "sz_key", "future", "done"])
RunningJob.__new__.__defaults__ = (False, )


class StopMode(Enum):
  """Holds the states options for the queue."""
  never = 0x01
  when_all_done = 0x02
  when_current_done = 0x04
  now = 0x08


class Queue(object):
  """The job manager."""
  # pylint: disable=too-many-instance-attributes
  def __init__(self, model_access, worker_count=10):
    """Initializes the Queue instance.

    :model_access: a bidon.data.ModelAccess instance
    :worker_count: the maximum number of workers to run at any one time
    """
    self._model_access = model_access
    self._worker_count = worker_count
    self._job_handlers = {}
    self._job_lock = Lock()
    self._executor = ThreadPoolExecutor(max_workers=worker_count)
    self._stop_mode = StopMode.never
    self._stop_callback = None
    self._waiting_job_count = 0
    self._running_jobs = {}

  def add_handler(self, name, handler):
    """Registers a function to handle jobs with a given name.

    :name: the job name to handle
    :handler: the function to handle the job. This function should accept a
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

    :callback: assign a callback to be called when the manager stops
    :stop_mode: an instance of the StopMode enum
    """
    if self._stop_mode.value < stop_mode.value:
      self._stop_callback = callback
      self._stop_mode = stop_mode
      LOGGER.info("Stop %s requested", stop_mode.name.replace("_", " "))

  def status(self):
    """Returns the current status of the JobQueue."""
    return dict(waiting_jobs=self._waiting_job_count,
                running_jobs=len(self._running_jobs),
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
      self._update_job_list()

      # If the stop mode is never, or when all are done, continue to add jobs
      if self._stop_mode in (StopMode.never, StopMode.when_all_done):
        self._start_jobs()

      if not self._running_jobs:
        if self._stop_mode == StopMode.when_current_done:
          break
        if self._stop_mode == StopMode.when_all_done and self._waiting_job_count == 0:
          break

      sleep(SLEEP)

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
      else:
        start_new_count = 0

  def _start_a_job(self):
    """Either starts a waiting job and returns a 3-tuple of (job, sz_key, future),
    or finds no waiting job and returns a 3-tuple of (None, None, None).
    """
    (job, sz_key) = self._get_next_job()

    if job is None:
      return (None, None, None)

    def fxn():
      """Future closure."""
      if job.name not in self._job_handlers:
        raise KeyError("Bad job name")
      self._job_handlers[job.name](job.payload)

    job.started_at = utc_now()
    if sz_key:
      sz_key.active_job_id = job.id

    with transaction(self._model_access):
      self._update_job(job, sz_key)

    future = self._executor.submit(fxn)
    future.add_done_callback(lambda _: self._mark_job_done(job.id))
    return (job, sz_key, future)

  def _get_next_job(self):
    """Returns a 2-tuple of (job, serialization_key) for the highest priority
    waiting job that has an open serialization key. Returns (None, None) if
    no such job exists.
    """
    job_data = self._model_access.find(
      "{} as j left join {} as k on j.serialization_key_id = k.id".format(
        Job.table_name,
        SerializationKey.table_name),
      "j.started_at is null and k.active_job_id is null",
      columns="j.*",
      order_by="j.priority desc, j.created_at asc")

    if job_data is None:
      return (None, None)

    job = Job(job_data)
    if job.serialization_key_id:
      sz_key = self._model_access.find_model_by_id(SerializationKey, job.serialization_key_id)
    else:
      sz_key = None

    return (job, sz_key)

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

    :job: the Job instance
    :sz_key: the SerializationKey instance
    :future: the Future instance that handled the job
    """
    error_message = exception_to_message(future.exception())
    job.update(completed_at=utc_now(), error_message=error_message)
    if sz_key:
      sz_key.active_job_id = None

    with transaction(self._model_access):
      self._update_job(job, sz_key)
