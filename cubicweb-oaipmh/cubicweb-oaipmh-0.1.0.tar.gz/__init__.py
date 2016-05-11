"""cubicweb-oaipmh application package

OAI-PMH server for CubicWeb
"""
from datetime import datetime

import pytz


def isodate(date=None):
    """Return a ISO string representation of a date."""
    if date is None:
        date = datetime.now(pytz.utc)
    date = date.replace(microsecond=0)
    if date.tzinfo is not None:
        date = date.astimezone(pytz.utc).replace(tzinfo=None)
    return date.isoformat() + 'Z'
