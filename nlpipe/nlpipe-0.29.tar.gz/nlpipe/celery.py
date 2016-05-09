from __future__ import absolute_import

import logging

from celery import Celery

logger = logging.getLogger(__name__)

app = Celery('nlpipe', include=['nlpipe.tasks'])
app.config_from_object('nlpipe.celeryconfig')

if __name__ == '__main__':
    app.start()
