from celery import shared_task
from .exceptions import UPSException
from .tnt import fetch_estimated_arrival_times
import logging


logger = logging.getLogger(__name__)


@shared_task(bind=True, throws=(UPSException, ))
def task_fetch_estimated_arrival_times(**kwargs):
    return fetch_estimated_arrival_times(**kwargs)
