from threading import Thread
from time import sleep
from unittest import TestCase

from bidon.db.access import ModelAccess
from bidon.db.core import get_pg_core

import pypgq
import pypgq.model as M


CONNECTION_STRING = None


def configure(database_name, port):
  from psycopg2.extras import Json
  from psycopg2.extensions import register_adapter

  global CONNECTION_STRING

  CONNECTION_STRING = "host=localhost port={} user=postgres dbname={}".format(port, database_name)

  register_adapter(dict, lambda d: Json(d))


def sleep_job(data):
  secs = float(data["seconds"])
  print("Starting to sleep for {}".format(secs))
  sleep(secs)
  print("Done sleeping")


def exception_job(data):
  raise Exception(data.get("message", "An exception :("))


class PyPGQueueTestCase(TestCase):
  def setUp(self):
    self.da = ModelAccess(get_pg_core(CONNECTION_STRING)).open(autocommit=True)
    self._clean_tables()

  def tearDown(self):
    self._clean_tables()

  def _clean_tables(self):
    self.da.update(M.SerializationKey.table_name, dict(active_job_id=None))
    self.da.delete(M.Job.table_name)
    self.da.delete(M.SerializationKey.table_name)

  def _table_counts(self):
    return (self.da.count(M.Job.table_name), self.da.count(M.SerializationKey.table_name))

  def test_queue_job(self):
    self.assertEqual(self._table_counts(), (0, 0))
    pypgq.queue_job(self.da, "Job A", dict(name="Trey", status="Start"))
    pypgq.queue_job(self.da, "Job B")
    pypgq.queue_job(self.da, "Job C", dict(name="Julie", status="In Progress"), "tenant/1")
    pypgq.queue_job(self.da, "Job D", None, "tenant/1")
    pypgq.queue_job(self.da, "Job E", None, "tenant/2")
    self.assertEqual(self._table_counts(), (5, 2))

  def test_run_jobs(self):
    qda = ModelAccess(get_pg_core(CONNECTION_STRING)).open(autocommit=True)
    queue = pypgq.Queue(
      qda,
      worker_count=2,
      cooperative=None)#pypgq.Cooperative(pypgq.Cooperative.advisory_lock, (1, 1)))
    queue._sleep_time = 1.0
    queue.add_handler("sleep_job", sleep_job)
    queue.add_handler("exception_job", exception_job)

    self.assertEqual(queue.status(),
                     {"waiting_jobs": 0,
                      "running_jobs": 0,
                      "running_job_ids": (),
                      "completed_jobs": 0,
                      "stop_mode": pypgq.StopMode.never})

    j1, _ = pypgq.queue_job(self.da, "sleep_job", {"seconds": 5})
    j2, _ = pypgq.queue_job(self.da, "sleep_job", {"seconds": 5})
    j3, _ = pypgq.queue_job(self.da, "exception_job", {"seconds": 5})

    sqt = Thread(target=queue.start)
    sqt.start()

    # NOTE: this is kind of tricy. We need to wait for the right intervals to check the status, and
    #       it's not easy to get right. The better result would be to have some kind of event system
    #       on the queue to call functions when it starts, stops, etc. jobs.
    sleep(2.5)
    self.assertEqual(queue.status(),
                     {"waiting_jobs": 1,
                      "running_jobs": 2,
                      "running_job_ids": (j1.id, j2.id),
                      "completed_jobs": 0,
                      "stop_mode": pypgq.StopMode.never})
    sleep(3.5)
    self.assertEqual(queue.status(),
                     {"waiting_jobs": 0,
                      "running_jobs": 1,
                      "running_job_ids": (j3.id, ),
                      "completed_jobs": 2,
                      "stop_mode": pypgq.StopMode.never})
    sleep(5.0)
    self.assertEqual(queue.status(),
                     {"waiting_jobs": 0,
                      "running_jobs": 0,
                      "running_job_ids": (),
                      "completed_jobs": 3,
                      "stop_mode": pypgq.StopMode.never})

    queue.stop(None, pypgq.StopMode.when_all_done)
    sqt.join()

  def test_job_serialization(self):
    qda = ModelAccess(get_pg_core(CONNECTION_STRING)).open(autocommit=True)
    queue = pypgq.Queue(qda, worker_count=2)
    queue._sleep_time = 1.0
    queue.add_handler("sleep_job", sleep_job)
    queue.add_handler("exception_job", exception_job)

    j1, _ = pypgq.queue_job(self.da, "sleep_job", {"seconds": 3}, "serialize")
    j2, _ = pypgq.queue_job(self.da, "sleep_job", {"seconds": 3}, "serialize")

    sqt = Thread(target=queue.start)
    sqt.start()

    sleep(1.5)
    self.assertEqual(queue.status(),
                     {"waiting_jobs": 1,
                      "running_jobs": 1,
                      "running_job_ids": (j1.id, ),
                      "completed_jobs": 0,
                      "stop_mode": pypgq.StopMode.never})
    sleep(3.0)
    self.assertEqual(queue.status(),
                     {"waiting_jobs": 0,
                     "running_jobs": 1,
                     "running_job_ids": (j2.id, ),
                     "completed_jobs": 1,
                     "stop_mode": pypgq.StopMode.never})
    sleep(2.0)
    self.assertEqual(queue.status(),
                     {"waiting_jobs": 0,
                      "running_jobs": 0,
                      "running_job_ids": (),
                      "completed_jobs": 2,
                      "stop_mode": pypgq.StopMode.never})

    queue.stop(None, pypgq.StopMode.when_all_done)
    sqt.join()
