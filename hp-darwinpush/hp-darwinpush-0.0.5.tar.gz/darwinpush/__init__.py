from enum import Enum
class Source(Enum):
    stomp = 1
    ftp_log = 2
    fpt_snapshot = 3

from darwinpush.client import Client
from darwinpush.listener import Listener
