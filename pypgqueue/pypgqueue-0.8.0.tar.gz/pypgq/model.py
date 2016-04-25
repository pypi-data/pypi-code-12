"""Models representing job queue tables."""
from bidon.db.model import ModelBase


class Job(ModelBase):
  """Model of a job."""
  table_name = "jobs"
  timestamps = ("created_at", None)
  attrs = dict(
    name=None,
    payload=None,
    priority=None,
    serialization_key_id=None,
    started_at=None,
    completed_at=None,
    error_message=None)


class SerializationKey(ModelBase):
  """Model of a serialization key. No two jobs with the same serialization key will run at the
  same time.
  """
  table_name = "serialization_keys"
  timestamps = None
  attrs = dict(key=None, active_job_id=None)
