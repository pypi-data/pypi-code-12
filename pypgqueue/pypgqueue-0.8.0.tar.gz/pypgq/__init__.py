"""A job queuer that uses PostgreSQL's pubsub functionality.

Features job serialization and prioritization.

Use this when you need job queuing functionality and you're already using Pythong and Postgres, and
you do not want to install a bunch of new dependencies.
"""
from .queue import Cooperative, Queue, StopMode
from .util import queue_job
