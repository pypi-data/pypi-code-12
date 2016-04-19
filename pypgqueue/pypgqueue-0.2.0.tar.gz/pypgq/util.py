"""Contains util methods for the module."""
import traceback

from .model import Job, SerializationKey


def queue_job(model_access, name, payload=None, serialization_key=None, *, priority=0):
  """Queues a job for a given connection.

  :model_access: a bidon.data.ModelAccess instance.
  :name: the name of the job.
  :payload: a dict that will be passed to the job.
  :serialization_key: the serialization key. If present a serialization key record will be created
                      if one does not exist for the key.
  :priority: the importance of the job, higher priority jobs will be run earlier.
  """
  if serialization_key:
    sz_key = model_access.find_model(SerializationKey, dict(key=serialization_key))
    if sz_key is None:
      sz_key = SerializationKey(key=serialization_key)
      model_access.insert_model(sz_key)
    job = Job(name=name,
              payload=payload,
              serialization_key_id=sz_key.id,
              priority=priority)
    model_access.insert_model(job)
  else:
    sz_key = None
    job = Job(name=name,
              payload=payload,
              serialization_key_id=None,
              priority=priority)
    model_access.insert_model(job)

  return (job, sz_key)


def exception_to_message(ex):
  """Converts an exception to a string."""
  if ex is None:
    return None
  ex_message = "Exception Type {0}: {1}".format(type(ex).__name__, ex)
  return ex_message + "\n" + "".join(traceback.format_tb(ex.__traceback__))
