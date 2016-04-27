"""Contains util methods for the module."""
import traceback

from .model import Job, ScheduledJob, SerializationKey


def queue_job(model_access, name, payload=None, serialization_key=None, *, priority=0,
              scheduled_at=None):
  """Queues a job for a given connection. If scheduled_at is given, then the job is scheduled to be
  queued later.

  :param model_access: a bidon.data.ModelAccess instance.
  :param name: the name of the job.
  :param payload: a dict that will be passed to the job.
  :param serialization_key: the serialization key. If present a serialization key record will be
                            created if one does not exist for the key.
  :param priority: the importance of the job, higher priority jobs will be run earlier.
  :param scheduled_at: a timestamp after which the job should be queued
  """
  if serialization_key:
    sz_key = model_access.find_model(SerializationKey, dict(key=serialization_key))
    if sz_key is None:
      sz_key = SerializationKey(key=serialization_key)
      model_access.insert_model(sz_key)
    job = _create_job(name, payload, sz_key.id, priority, scheduled_at)
    model_access.insert_model(job)
  else:
    sz_key = None
    job = _create_job(name, payload, None, priority, scheduled_at)
    model_access.insert_model(job)

  return (job, sz_key)


def exception_to_message(ex):
  """Converts an exception to a string.

  :param ex: an exception instance
  """
  if ex is None:
    return None
  ex_message = "Exception Type {0}: {1}".format(type(ex).__name__, ex)
  return ex_message + "\n" + "".join(traceback.format_tb(ex.__traceback__))


def _create_job(name, payload, serialization_key_id, priority, scheduled_at):
  """Cretes either a Job model or a ScheduledJob model, depending on the presence of scheduled_at.
  """
  if scheduled_at is None:
    return Job(name=name,
               payload=payload,
               serialization_key_id=serialization_key_id,
               priority=priority)
  else:
    return ScheduledJob(name=name,
                        payload=payload,
                        serialization_key_id=serialization_key_id,
                        priority=priority,
                        scheduled_at=scheduled_at)
