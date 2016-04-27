import logging,os
from rest import Restclient

LOCAL_DATA_FOLDER = '/DATA'
GENOTYPE_FOLDER = '/GENOTYPE'

REST_HOST = os.environ['REST_HOST']
REST_USERNAME = os.environ['REST_USERNAME']
REST_PASSWORD = os.environ['REST_PASSWORD']

restclient = Restclient(REST_HOST,REST_USERNAME,REST_PASSWORD)

class CeleryProgressLogHandler(logging.StreamHandler):

    def __init__(self,task):
        logging.StreamHandler.__init__(self)
        self.task = task
    
    def emit(self,record):
        if 'progress' in record.__dict__:
            progress = record.__dict__['progress']
            msg = self.format(record)
            if 'task' in record.__dict__:
                msg = record.__dict__['task']
            body = {'progress':progress,'task':msg}
            self.task.update_state(state='PROGRESS',meta=body)
